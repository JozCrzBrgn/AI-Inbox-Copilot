import json
from unittest.mock import MagicMock, patch


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('backend.services.email_analizer.get_settings')
@patch('backend.services.email_analizer.openai.chat.completions.create')
@patch('backend.services.email_analizer.prompt_manager')
def test_analyze_email_successful_response(mock_prompt_manager, mock_openai, mock_get_settings):
    # Mock config
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_model = "gpt-test"
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_settings.ai_agent.openai_temperature = 0
    mock_settings.ai_agent.openai_max_tokens = 100

    mock_get_settings.return_value = mock_settings

    # Prompt
    mock_prompt_manager.get_analysis_prompt.return_value = "System prompt (mocked)"

    # Fake OpenAI response
    fake_response = {
        "customer_name": "John",
        "intent": "support_request",
        "summary": "Needs help",
        "priority": "high",
        "sentiment": "neutral",
        "suggested_subject": "Help",
        "suggested_reply": "We will help you"
    }

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps(fake_response)

    mock_openai.return_value = mock_resp

    from backend.services.email_analizer import analyze_email

    result = analyze_email("Help me")

    assert result["intent"] == "support_request"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('backend.services.email_analizer.get_settings')
@patch('backend.services.email_analizer.openai.chat.completions.create')
@patch('backend.services.email_analizer.prompt_manager')
def test_json_with_markdown(mock_prompt_manager, mock_openai, mock_get_settings):
    """JSON with markdown (cleaning)"""

    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_model = "gpt-test"
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_settings.ai_agent.openai_temperature = 0
    mock_settings.ai_agent.openai_max_tokens = 100
    mock_get_settings.return_value = mock_settings

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

    from backend.services.email_analizer import analyze_email

    result = analyze_email("Bad service")

    assert result["customer_name"] == "Ana"
    assert result["intent"] == "complaint"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('backend.services.email_analizer.get_settings')
@patch('backend.services.email_analizer.openai.chat.completions.create')
@patch('backend.services.email_analizer.prompt_manager')
def test_malformed_json_extraction(mock_prompt_manager, mock_openai, mock_get_settings):
    """Malformed JSON (use extractor)"""

    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    malformed = 'Text before {"customer_name": "Luis", "intent": "support_request"} text after'

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = malformed

    mock_openai.return_value = mock_resp

    from backend.services.email_analizer import analyze_email

    result = analyze_email("Help")

    assert result["customer_name"] == "Luis"
    assert result["intent"] == "support_request"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('backend.services.email_analizer.get_settings')
@patch('backend.services.email_analizer.openai.chat.completions.create')
@patch('backend.services.email_analizer.prompt_manager')
def test_invalid_values_normalization(mock_prompt_manager, mock_openai, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    bad_response = {
        "customer_name": "Maria",
        "intent": "info",
        "summary": "Info",
        "priority": "urgent",  #  → invalid
        "sentiment": "angry",  #  → invalid
        "suggested_subject": "Info",
        "suggested_reply": "Reply"
    }

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps(bad_response)

    mock_openai.return_value = mock_resp

    from backend.services.email_analizer import analyze_email

    result = analyze_email("Info")

    assert result["priority"] == "medium"
    assert result["sentiment"] == "neutral"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('backend.services.email_analizer.get_settings')
@patch('backend.services.email_analizer.openai.chat.completions.create')
@patch('backend.services.email_analizer.prompt_manager')
def test_openai_exception_returns_default(mock_prompt_manager, mock_openai, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    mock_openai.side_effect = Exception("API failure")

    from backend.services.email_analizer import analyze_email

    result = analyze_email("Anything")

    assert result["intent"] == "unknown"
    assert result["customer_name"] == "Unknown"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('backend.services.email_analizer.get_settings')
@patch('backend.services.email_analizer.openai.chat.completions.create')
@patch('backend.services.email_analizer.prompt_manager')
def test_missing_fields_are_filled(mock_prompt_manager, mock_openai, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    partial_response = {
        "intent": "support_request"
    }

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps(partial_response)

    mock_openai.return_value = mock_resp

    from backend.services.email_analizer import analyze_email

    result = analyze_email("Help")

    assert result["customer_name"] == "Not specified"
    assert result["intent"] == "support_request"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('backend.services.email_analizer.get_settings')
@patch('backend.services.email_analizer.openai.chat.completions.create')
@patch('backend.services.email_analizer.prompt_manager')
def test_invalid_json_returns_default(mock_prompt_manager, mock_openai, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = "not a json at all"

    mock_openai.return_value = mock_resp

    from backend.services.email_analizer import analyze_email

    result = analyze_email("Hello")

    assert result["intent"] == "unknown"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('backend.services.email_analizer.get_settings')
@patch('backend.services.email_analizer.openai.chat.completions.create')
@patch('backend.services.email_analizer.prompt_manager')
def test_markdown_without_json_keyword(mock_prompt_manager, mock_openai, mock_get_settings):
    """Response with ``` without json keyword"""

    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    content = """```
    {"customer_name": "Pedro", "intent": "support_request"}
    ```"""

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = content

    mock_openai.return_value = mock_resp

    from backend.services.email_analizer import analyze_email

    result = analyze_email("Help")

    assert result["customer_name"] == "Pedro"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('backend.services.email_analizer.get_settings')
@patch('backend.services.email_analizer.openai.chat.completions.create')
@patch('backend.services.email_analizer.prompt_manager')
def test_json_with_noise_around(mock_prompt_manager, mock_openai, mock_get_settings):
    """JSON with garbage text before and after"""

    mock_settings = MagicMock()
    mock_settings.ai_agent.openai_api_key = "sk-proj-more_caracteres"
    mock_get_settings.return_value = mock_settings

    mock_prompt_manager.get_analysis_prompt.return_value = "mock prompt"

    noisy = "random text {\"customer_name\": \"Luis\", \"intent\": \"support_request\"} more text"

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = noisy

    mock_openai.return_value = mock_resp

    from backend.services.email_analizer import analyze_email

    result = analyze_email("Help")

    assert result["customer_name"] == "Luis"