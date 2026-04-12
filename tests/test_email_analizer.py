import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.exceptions import HTTPException

from backend.services.email_analizer import analyze_email


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_analyze_email_successful_response(
    mock_detect_injection,
    mock_classify_intent,
    mock_is_support,
    mock_sanitize,
    mock_prompt_manager,
    mock_openai,
    mock_get_settings,
):
    # Mock config
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_model = "gpt-test"
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_settings.ai_agent.openai_temperature = 0
    mock_settings.ai_agent.openai_max_tokens = 100
    mock_get_settings.return_value = mock_settings

    # Mock security validations
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "Help me please",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify_intent.return_value = {"category": "SUPPORT"}
    mock_detect_injection.return_value = {"is_manipulation": False, "confidence": 0}

    # Mock prompt
    mock_prompt_manager.get_analysis_prompt.return_value = "System prompt (mocked)"

    # Fake OpenAI response
    fake_response = {
        "customer_name": "John",
        "intent": "support_request",
        "summary": "Needs help",
        "priority": "high",
        "sentiment": "neutral",
        "suggested_subject": "Help",
        "suggested_reply": "We will help you",
    }

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps(fake_response)

    mock_openai.return_value = mock_resp

    result = analyze_email("Help me", "John")

    assert result["intent"] == "support_request"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_json_with_markdown(
    mock_detect_injection,
    mock_classify_intent,
    mock_is_support,
    mock_sanitize,
    mock_prompt_manager,
    mock_openai,
    mock_get_settings,
):
    """JSON with markdown (cleaning)"""

    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_model = "gpt-test"
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_settings.ai_agent.openai_temperature = 0
    mock_settings.ai_agent.openai_max_tokens = 100
    mock_get_settings.return_value = mock_settings

    # Mock security validations
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "Bad service",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify_intent.return_value = {"category": "SUPPORT"}
    mock_detect_injection.return_value = {"is_manipulation": False, "confidence": 0}

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    content = """```json
    {"customer_name": "Ana", "intent": "complaint", "summary": "Bad service", 
    "priority": "high", "sentiment": "negative", 
    "suggested_subject": "Complaint", "suggested_reply": "Sorry"}
    ```"""

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = content

    mock_openai.return_value = mock_resp

    result = analyze_email("Bad service", "Ana")

    assert result["customer_name"] == "Ana"
    assert result["intent"] == "complaint"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_malformed_json_extraction(
    mock_detect_injection,
    mock_classify_intent,
    mock_is_support,
    mock_sanitize,
    mock_prompt_manager,
    mock_openai,
    mock_get_settings,
):
    """Malformed JSON (use extractor)"""

    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    # Mock security validations
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "Help",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify_intent.return_value = {"category": "SUPPORT"}
    mock_detect_injection.return_value = {"is_manipulation": False, "confidence": 0}

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    malformed = (
        'Text before {"customer_name": "Luis", "intent": "support_request"} text after'
    )

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = malformed

    mock_openai.return_value = mock_resp

    result = analyze_email("Help", "Luis")

    assert result["customer_name"] == "Luis"
    assert result["intent"] == "support_request"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_invalid_values_normalization(
    mock_detect_injection,
    mock_classify_intent,
    mock_is_support,
    mock_sanitize,
    mock_prompt_manager,
    mock_openai,
    mock_get_settings,
):
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    # Mock security validations
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "Info",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify_intent.return_value = {"category": "SUPPORT"}
    mock_detect_injection.return_value = {"is_manipulation": False, "confidence": 0}

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    bad_response = {
        "customer_name": "Maria",
        "intent": "info",
        "summary": "Info",
        "priority": "urgent",
        "sentiment": "angry",
        "suggested_subject": "Info",
        "suggested_reply": "Reply",
    }

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps(bad_response)

    mock_openai.return_value = mock_resp

    result = analyze_email("Info", "Maria")

    assert result["priority"] == "medium"
    assert result["sentiment"] == "neutral"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
def test_openai_exception_returns_default(
    mock_classify_intent,
    mock_is_support,
    mock_sanitize,
    mock_prompt_manager,
    mock_openai,
    mock_get_settings,
):
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    # Mock security validations
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "Anything",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify_intent.return_value = {"category": "SUPPORT"}

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    mock_openai.side_effect = Exception("API failure")

    with pytest.raises(HTTPException) as exc_info:
        analyze_email("Anything", "Juan")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "AI processing failed"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_missing_fields_are_filled(
    mock_detect_injection,
    mock_classify_intent,
    mock_is_support,
    mock_sanitize,
    mock_prompt_manager,
    mock_openai,
    mock_get_settings,
):
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    # Mock security validations
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "Help",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify_intent.return_value = {"category": "SUPPORT"}
    mock_detect_injection.return_value = {"is_manipulation": False, "confidence": 0}

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    partial_response = {"intent": "support_request"}

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps(partial_response)

    mock_openai.return_value = mock_resp

    result = analyze_email("Help", "Juan")

    assert result["customer_name"] == "Unknown"
    assert result["intent"] == "support_request"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_invalid_json_returns_default(
    mock_detect_injection,
    mock_classify_intent,
    mock_is_support,
    mock_sanitize,
    mock_prompt_manager,
    mock_openai,
    mock_get_settings,
):
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    # Mock security validations
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "Hello",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify_intent.return_value = {"category": "SUPPORT"}
    mock_detect_injection.return_value = {"is_manipulation": False, "confidence": 0}

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = "not a json at all"

    mock_openai.return_value = mock_resp

    result = analyze_email("Hello", "Juan")

    assert result["intent"] == "unknown"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_markdown_without_json_keyword(
    mock_detect_injection,
    mock_classify_intent,
    mock_is_support,
    mock_sanitize,
    mock_prompt_manager,
    mock_openai,
    mock_get_settings,
):
    """Response with ``` without json keyword"""

    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    # Mock security validations
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "Help",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify_intent.return_value = {"category": "SUPPORT"}
    mock_detect_injection.return_value = {"is_manipulation": False, "confidence": 0}

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    content = """```
    {"customer_name": "Pedro", "intent": "support_request"}
    ```"""

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = content

    mock_openai.return_value = mock_resp

    result = analyze_email("Help", "Pedro")

    assert result["customer_name"] == "Pedro"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_json_with_noise_around(
    mock_detect_injection,
    mock_classify_intent,
    mock_is_support,
    mock_sanitize,
    mock_prompt_manager,
    mock_openai,
    mock_get_settings,
):
    """JSON with garbage text before and after"""

    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    # Mock security validations
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "Help",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify_intent.return_value = {"category": "SUPPORT"}
    mock_detect_injection.return_value = {"is_manipulation": False, "confidence": 0}

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    noisy = (
        'random text {"customer_name": "Luis", "intent": "support_request"} more text'
    )

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = noisy

    mock_openai.return_value = mock_resp

    result = analyze_email("Help", "Luis")

    assert result["customer_name"] == "Luis"


def test_empty_input_returns_security_violation():
    result = analyze_email("", "Juan")

    assert result["intent"] == "security_violation"
    assert "Empty or invalid input" in result["summary"]


@patch("backend.services.email_analizer.sanitize_and_validate")
def test_sanitize_blocks_input(mock_sanitize):
    mock_sanitize.return_value = {
        "should_block": True,
        "safe_text": "",
        "injection_report": {"confidence": 0.9, "detected_patterns": ["hack"]},
    }

    result = analyze_email("malicious", "Juan")

    assert result["intent"] == "security_violation"
    assert "Prompt injection detected" in result["summary"]


@patch("backend.services.email_analizer.sanitize_and_validate")
def test_empty_after_sanitize(mock_sanitize):
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }

    result = analyze_email("something", "Juan")

    assert result["intent"] == "security_violation"
    assert "Invalid content after sanitization" in result["summary"]


@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
def test_not_support_email(mock_is_support, mock_sanitize):
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "random text",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = False

    result = analyze_email("random", "Juan")

    assert result["intent"] == "security_violation"
    assert "INVALID_INPUT" in result["summary"]


@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
def test_non_support_classification(mock_classify, mock_is_support, mock_sanitize):
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "marketing email",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify.return_value = {"category": "MARKETING"}

    result = analyze_email("promo", "Juan")

    assert result["intent"] == "non_support_marketing"


@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_llm_detects_injection(
    mock_detect, mock_classify, mock_is_support, mock_sanitize
):
    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "help",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify.return_value = {"category": "SUPPORT"}
    mock_detect.return_value = {
        "is_manipulation": True,
        "confidence": 0.9,
        "reason": "prompt injection",
    }

    result = analyze_email("help", "Juan")

    assert result["intent"] == "security_violation"
    assert "Semantic injection detected" in result["summary"]


@patch("backend.services.email_analizer.get_settings")
@patch("backend.services.email_analizer.openai.chat.completions.create")
@patch("backend.services.email_analizer.prompt_manager")
@patch("backend.services.email_analizer.sanitize_and_validate")
@patch("backend.services.email_analizer.is_email_support")
@patch("backend.services.email_analizer.classify_intent_cheap")
@patch("backend.services.email_analizer.detect_injection_with_llm")
def test_use_examples_true(
    mock_detect,
    mock_classify,
    mock_is_support,
    mock_sanitize,
    mock_prompt,
    mock_openai,
    mock_settings,
):
    mock_settings.return_value.ai_agent.openai_model = "test"
    mock_settings.return_value.ai_agent.openai_api_key = "key"
    mock_settings.return_value.ai_agent.openai_temperature = 0
    mock_settings.return_value.ai_agent.openai_max_tokens = 10

    mock_sanitize.return_value = {
        "should_block": False,
        "safe_text": "help",
        "injection_report": {"confidence": 0, "detected_patterns": []},
    }
    mock_is_support.return_value = True
    mock_classify.return_value = {"category": "SUPPORT"}
    mock_detect.return_value = {"is_manipulation": False, "confidence": 0}

    mock_prompt.get_analysis_prompt.return_value = "prompt"

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps({"intent": "support"})
    mock_openai.return_value = mock_resp

    analyze_email("help", "Juan", use_examples=True)

    mock_prompt.get_analysis_prompt.assert_called_with(
        "help", include_examples=True, max_examples=2
    )
