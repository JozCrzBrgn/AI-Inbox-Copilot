import json
import logging

import openai

from prompts import prompt_manager

from ..core.config import get_settings

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
        # Get the manager prompt (with or without examples)
        if use_examples:
            system_prompt = prompt_manager.get_analysis_prompt(
                email_content, 
                include_examples=True,
                max_examples=2  # Limit to 2 examples to avoid exceeding tokens
            )
        else:
            system_prompt = prompt_manager.get_analysis_prompt(email_content)
        
        cnf = get_settings()
        
        # Configure API key
        openai.api_key = cnf.ai_agent.openai_api_key
        logger.info(f"Analyzing email with model: {cnf.ai_agent.openai_model}")
        
        response = openai.chat.completions.create(
            model=cnf.ai_agent.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Email to analyze:\n\n{email_content}"}
            ],
            temperature=cnf.ai_agent.openai_temperature,
            max_tokens=cnf.ai_agent.openai_max_tokens
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
    
    except Exception as e:
        logger.error(f"Error analyzing email: {e}", exc_info=True)
        return _get_default_result()


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
    if text.startswith('{') and text.endswith('}'):
        return text
    
    # Find the first { and last }
    start = text.find('{')
    end = text.rfind('}')
    
    if start != -1 and end != -1:
        return text[start:end+1]
    
    return text


def _extract_json_from_text(text: str) -> dict:
    """Try extracting JSON from incorrectly formatted text"""
    import re
    
    # Search for JSON patterns
    json_pattern = r'\{[^{}]*\}'
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
        "customer_name", "intent", "summary", 
        "priority", "sentiment", "suggested_subject", "suggested_reply"
    ]
    
    # Ensure that all fields exist
    normalized = {}
    for field in required_fields:
        normalized[field] = result.get(field, "Not specified")
    
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
        "suggested_reply": "Thank you for your email. Our team will review your message and get back to you shortly."
    }