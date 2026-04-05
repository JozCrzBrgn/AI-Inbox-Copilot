import importlib
import os
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.abspath("frontend"))


import pytest


class MockChoice:
    def __init__(self, content):
        self.message = type("obj", (), {"content": content})


class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]


@pytest.fixture
def mock_openai_success(monkeypatch):
    def mock_create(*args, **kwargs):
        return MockResponse('{"category": "SUPPORT", "confidence": 0.9}')

    monkeypatch.setattr("openai.chat.completions.create", mock_create)


@pytest.fixture
def mock_openai_injection(monkeypatch):
    def mock_create(*args, **kwargs):
        return MockResponse(
            '{"is_manipulation": true, "confidence": 0.8, "reason": "forced format"}'
        )

    monkeypatch.setattr("openai.chat.completions.create", mock_create)


@pytest.fixture
def mock_openai_error(monkeypatch):
    def mock_create(*args, **kwargs):
        raise Exception("API error")

    monkeypatch.setattr("openai.chat.completions.create", mock_create)


@pytest.fixture
def mock_settings(monkeypatch):
    class MockAI:
        openai_api_key = "fake-key"
        openai_cheap_model = "fake-model"
        openai_cheap_temperature = 0.0
        openai_cheap_max_tokens = 50

    class MockAPIInfo:
        name = "Test API"
        description = "Test Desc"
        version = "1.0"
        contact_name = "Test"
        contact_email = "test@test.com"
        contact_url = "http://test.com"
        license = "MIT"
        license_url = "http://license.com"

    class MockCORS:
        cors_allow_origins = ["*"]
        cors_allow_methods = ["*"]
        cors_allow_headers = ["*"]

    class MockSettings:
        ai_agent = MockAI()
        api_info = MockAPIInfo()
        cors = MockCORS()

    monkeypatch.setattr("backend.core.config.get_settings", lambda: MockSettings())


@pytest.fixture
def mock_db(monkeypatch):
    monkeypatch.setattr("backend.services.database.init_database", lambda: None)


@pytest.fixture
def app_client(mock_settings, mock_db):
    import backend.main

    importlib.reload(backend.main)

    return TestClient(backend.main.app)
