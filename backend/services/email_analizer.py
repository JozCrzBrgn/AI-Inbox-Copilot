import json
import logging

import openai
from fastapi.exceptions import HTTPException

from backend.services.redis_client import (
    _cache_get,
    _cache_set,
    _check_token_budget,
    _estimate_tokens,
    _hash,
)
from prompts import prompt_manager

from ..core.config import get_settings
from .prompt_security import (
    classify_intent_cheap,
    detect_injection_with_llm,
    is_email_support,
    sanitize_and_validate,
)

logger = logging.getLogger(__name__)


def analyze_email(
    email_content: str, username: str, use_examples: bool = False
) -> dict:
    """
    Analyze an email using OpenAI and return a dictionary with the insights

    Args:
        email_content: The content of the email to be analyzed
        use_examples: Boolean variable indicating whether to include few-shot examples in the prompt

    Returns:
        Dictionary with the analyzed fields
    """
    try:
        if not email_content or not isinstance(email_content, str):
            return _get_security_violation_result("Empty or invalid input")

        # 1. SANITIZE + DETECT
        validation = sanitize_and_validate(email_content)

        if validation["should_block"]:
            content_hash = _hash(email_content)
            _cache_set(f"blocked:{content_hash}", True, ttl=600)

            logger.warning("BLOCKED input detected")
            return _get_security_violation_result("Prompt injection detected")

        cleaned_content = validation["safe_text"]

        if not cleaned_content:
            return _get_security_violation_result("Invalid content after sanitization")

        content_hash = _hash(cleaned_content)

        # 2. VALIDATE SUPPORT EMAIL
        if not is_email_support(cleaned_content):
            return _get_security_violation_result("INVALID_INPUT")

        # 3. CACHE FINAL RESULT
        cache_key = f"analysis:v1:{content_hash}"
        cached = _cache_get(cache_key)
        if cached:
            logger.info("Cache HIT (analysis)")
            return cached

        # 4. CHEAP CLASSIFIER (CACHE)
        intent_key = f"intent:{content_hash}"
        cheap_result = _cache_get(intent_key)

        if not cheap_result:
            cheap_result = classify_intent_cheap(cleaned_content)
            _cache_set(intent_key, cheap_result, ttl=3600)
        else:
            logger.info("Cache HIT (intent)")

        if cheap_result.get("category") != "SUPPORT":
            return _get_non_support_result(cheap_result)

        # 5. INJECTION LLM (CACHE)
        inj_key = f"injection:{content_hash}"
        llm_injection_check = _cache_get(inj_key)

        if not llm_injection_check:
            llm_injection_check = detect_injection_with_llm(cleaned_content)
            _cache_set(inj_key, llm_injection_check, ttl=3600)
        else:
            logger.info("Cache HIT (injection)")

        if (
            llm_injection_check["is_manipulation"]
            and llm_injection_check["confidence"] >= 0.7
        ):
            return _get_security_violation_result(
                f"Semantic injection detected: {llm_injection_check['reason']}"
            )

        # 6. PROMPT
        if use_examples:
            system_prompt = prompt_manager.get_analysis_prompt(
                cleaned_content,
                include_examples=True,
                max_examples=2,
            )
        else:
            system_prompt = prompt_manager.get_analysis_prompt(cleaned_content)

        cnf = get_settings()
        openai.api_key = cnf.ai_agent.openai_api_key

        # 7. TOKEN BUDGET PER USER
        estimated_tokens = (
            _estimate_tokens(cleaned_content + system_prompt)
            + cnf.ai_agent.openai_max_tokens
        )

        _check_token_budget(username, estimated_tokens)

        # 8. OPENAI CALL
        response = openai.chat.completions.create(
            model=cnf.ai_agent.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Email to analyze:\n\n{cleaned_content}"},
            ],
            temperature=cnf.ai_agent.openai_temperature,
            max_tokens=cnf.ai_agent.openai_max_tokens,
        )

        result_text = response.choices[0].message.content
        result_text = _clean_json_response(result_text)

        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = _extract_json_from_text(result_text)

        result = _normalize_result(result)

        # 9. FINAL CACHE
        _cache_set(cache_key, result, ttl=21600)

        logger.info(f"Email analyzed: {result.get('intent')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI processing failed")


# ------------------ HELPERS ------------------ #


def _get_security_violation_result(reason: str) -> dict:
    """
    Returns a result for security violations
    """
    logger.warning(f"Security violation: {reason}")
    return {
        "customer_name": "Unknown",
        "intent": "security_violation",
        "summary": f"Security validation failed: {reason}",
        "priority": "low",
        "sentiment": "neutral",
        "suggested_subject": "Unable to process request",
        "suggested_reply": "We are unable to process this request due to security validation.",
    }


def _clean_json_response(text: str) -> str:
    """Clean the response to extract only the JSON."""
    # Remove markdown json
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    # Remove any text before or after
    text = text.strip()

    # Make sure it starts and ends with keys
    if text.startswith("{") and text.endswith("}"):
        return text

    # Find the first { and last }
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        return text[start : end + 1]

    return text


def _extract_json_from_text(text: str) -> dict:
    """Try extracting JSON from incorrectly formatted text"""
    import re

    # Search for JSON patterns
    json_pattern = r"\{[^{}]*\}"
    matches = re.findall(json_pattern, text)

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    # If no valid JSON is found, return the default result.
    return _get_default_result()


def _normalize_result(result: dict) -> dict:
    """Normalize and validate the result"""
    required_fields = [
        "customer_name",
        "intent",
        "summary",
        "priority",
        "sentiment",
        "suggested_subject",
        "suggested_reply",
    ]

    # Ensure that all fields exist
    normalized = {}
    for field in required_fields:
        val = result.get(field)
        if val is None:
            val = "Unknown" if field == "customer_name" else "Not specified"
        normalized[field] = str(val)

    if normalized["priority"].lower() not in ["low", "medium", "high"]:
        normalized["priority"] = "medium"

    if normalized["sentiment"].lower() not in ["positive", "neutral", "negative"]:
        normalized["sentiment"] = "neutral"

    return normalized


def _get_default_result() -> dict:
    """Returns default result in case of error"""
    return {
        "customer_name": "Unknown",
        "intent": "unknown",
        "summary": "Error analyzing email",
        "priority": "medium",
        "sentiment": "neutral",
        "suggested_subject": "Re: Your inquiry",
        "suggested_reply": "Thank you for your email. Our team will review your message and get back to you shortly.",
    }


def _get_non_support_result(classification: dict) -> dict:
    """Returns results for emails that are not supported"""
    category = classification.get("category", "OTHER")

    return {
        "customer_name": "Unknown",
        "intent": f"non_support_{category.lower()}",
        "summary": f"This message was classified as {category}",
        "priority": "low",
        "sentiment": "neutral",
        "suggested_subject": "Message received",
        "suggested_reply": "Thank you for your message.",
    }
