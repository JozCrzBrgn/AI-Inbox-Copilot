import pytest

from backend.core.ai_agent import AiAgentSettings


def test_api_key_empty():
    with pytest.raises(ValueError):
        AiAgentSettings(
            openai_api_key="",
            openai_model="gpt-4",
            openai_temperature=1.0,
            openai_max_tokens=100,
            openai_timeout=30
        )


def test_api_key_invalid_prefix():
    with pytest.raises(ValueError):
        AiAgentSettings(
            openai_api_key="abc12345678901234567890",
            openai_model="gpt-4",
            openai_temperature=1.0,
            openai_max_tokens=100,
            openai_timeout=30
        )


def test_invalid_model():
    with pytest.raises(ValueError):
        AiAgentSettings(
            openai_api_key="sk-12345678901234567890",
            openai_model="invalid-model",
            openai_temperature=1.0,
            openai_max_tokens=100,
            openai_timeout=30
        )


def test_temperature_out_of_range():
    with pytest.raises(ValueError):
        AiAgentSettings(
            openai_api_key="sk-12345678901234567890",
            openai_model="gpt-4",
            openai_temperature=3.0,
            openai_max_tokens=100,
            openai_timeout=30
        )


def test_max_tokens_invalid():
    with pytest.raises(ValueError):
        AiAgentSettings(
            openai_api_key="sk-12345678901234567890",
            openai_model="gpt-4",
            openai_temperature=1.0,
            openai_max_tokens=0,
            openai_timeout=30
        )


def test_max_tokens_too_large():
    with pytest.raises(ValueError):
        AiAgentSettings(
            openai_api_key="sk-12345678901234567890",
            openai_model="gpt-4",
            openai_temperature=1.0,
            openai_max_tokens=600,
            openai_timeout=30
        )