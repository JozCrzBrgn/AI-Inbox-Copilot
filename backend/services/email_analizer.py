import json
import logging

import openai
from fastapi.exceptions import HTTPException

from prompts import prompt_manager

from ..core.config import get_settings
from .prompt_security import (
    classify_intent_cheap,
    detect_injection_with_llm,
    is_email_support,
    sanitize_and_validate,
)

# Configure logging
logger = logging.getLogger(__name__)


def analyze_email(email_content: str, use_examples: bool = False) -> dict:
    """
    Analyze an email using OpenAI and return a dictionary with the insights

    Args:
        email_content: The content of the email to be analyzed
        use_examples: Boolean variable indicating whether to include few-shot examples in the prompt

    Returns:
        Dictionary with the analyzed fields
    """
    try:
        # Security checks
        # 1. Validate that it is a support email
        if not email_content or not isinstance(email_content, str):
            return _get_security_violation_result("Empty or invalid input")
        else:
            logger.info("Email content is valid, first validation passed")

        # 2. Detection + cleaning + blocking decision (single place)
        validation = sanitize_and_validate(email_content)

        if validation["should_block"]:
            logger.warning(
                f"Input LOCKED. Confidence: {validation['injection_report']['confidence']}, "
                f"Patterns: {validation['injection_report']['detected_patterns']}"
            )
            return _get_security_violation_result("Prompt injection detected")
        else:
            logger.info("Email content is valid, second validation passed")

        cleaned_content = validation["safe_text"]
        if not cleaned_content:
            logger.warning("Content became empty after cleaning")
            return _get_security_violation_result("Invalid content after sanitization")
        else:
            logger.info("Email content is valid, third validation passed")

        # 3. Validate that it is a support email (on clean text)
        if not is_email_support(cleaned_content):
            logger.warning("The input does not seem to be a support email")
            return _get_security_violation_result("INVALID_INPUT")
        else:
            logger.info("Email content is valid, fourth validation passed")

        # 4. Cheap classification (on clean text)
        cheap_result = classify_intent_cheap(cleaned_content)

        if cheap_result.get("category") != "SUPPORT":
            logger.info(
                f"Pre-qualification: {cheap_result.get('category')} — skipping full analysis"
            )
            return _get_non_support_result(cheap_result)
        else:
            logger.info("Email content is valid, fifth validation passed")

        # 5. Semantic validation with cheap LLM
        llm_injection_check = detect_injection_with_llm(cleaned_content)
        if (
            llm_injection_check["is_manipulation"]
            and llm_injection_check["confidence"] >= 0.7
        ):
            logger.warning(
                f"LLM detected semantic manipulation."
                f"Confidence: {llm_injection_check['confidence']}, "
                f"Reason: {llm_injection_check['reason']}"
            )
            return _get_security_violation_result(
                f"Semantic injection detected: {llm_injection_check['reason']}"
            )
        else:
            logger.info("Email content is valid, sixth validation passed")

        # Get the manager prompt (with or without examples)
        if use_examples:
            system_prompt = prompt_manager.get_analysis_prompt(
                cleaned_content,
                include_examples=True,
                max_examples=2,
            )
        else:
            system_prompt = prompt_manager.get_analysis_prompt(cleaned_content)

        # Configure API key
        cnf = get_settings()
        openai.api_key = cnf.ai_agent.openai_api_key
        logger.info(f"Analyzing email with model: {cnf.ai_agent.openai_model}")

        response = openai.chat.completions.create(
            model=cnf.ai_agent.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Email to analyze:\n\n{cleaned_content}"},
            ],
            temperature=cnf.ai_agent.openai_temperature,
            max_tokens=cnf.ai_agent.openai_max_tokens,
        )

        # Extract and parse the JSON from the response
        result_text = response.choices[0].message.content
        logger.debug(f"Raw response: {result_text[:200]}...")

        # Clean up any markdown or extra text
        result_text = _clean_json_response(result_text)

        try:
            result = json.loads(result_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            # Try to extract JSON from the response if there is additional text
            result = _extract_json_from_text(result_text)

        # Validate and normalize the result
        result = _normalize_result(result)

        logger.info(f"Email analyzed successfully: {result.get('intent', 'unknown')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI processing failed")


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

    # Normalize specific values
    valid_priorities = ["low", "medium", "high"]
    if normalized["priority"].lower() not in valid_priorities:
        normalized["priority"] = "medium"

    valid_sentiments = ["positive", "neutral", "negative"]
    if normalized["sentiment"].lower() not in valid_sentiments:
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
        "summary": f"This message was classified as {category} and does not require customer support action.",
        "priority": "low",
        "sentiment": "neutral",
        "suggested_subject": "Message received",
        "suggested_reply": "Thank you for your message. If you need customer support, please contact us at support@example.com",
    }
