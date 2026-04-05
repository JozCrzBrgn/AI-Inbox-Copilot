import asyncio

from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request


def test_app_starts(app_client):
    response = app_client.get("/docs")
    assert response.status_code == 200


def test_lifespan_calls_db(monkeypatch, mock_settings):
    called = {"db": False}

    def mock_init():
        called["db"] = True

    # Patch the reference inside backend.main instead of backend.services.database
    monkeypatch.setattr("backend.main.init_database", mock_init)

    from backend.main import app

    with TestClient(app):
        pass

    assert called["db"] is True


def test_rate_limit_handler(app_client):
    handler = app_client.app.exception_handlers[RateLimitExceeded]

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
    }

    request = Request(scope)

    class DummyExc:
        detail = "Rate limit exceeded"

    response = asyncio.run(handler(request, DummyExc()))

    assert response.status_code == 429


def test_cors_headers(app_client):
    response = app_client.options(
        "/",
        headers={
            "Origin": "http://test.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers


def test_middlewares_registered(app_client):
    middleware_names = [m.cls.__name__ for m in app_client.app.user_middleware]

    assert "CORSMiddleware" in middleware_names
    assert "SlowAPIMiddleware" in middleware_names


def test_routes_loaded(app_client):
    routes = [route.path for route in app_client.app.routes]

    assert "/health" in routes or any("health" in r for r in routes)

    assert any("/v1" in r for r in routes)


def test_app_metadata(app_client):
    app = app_client.app

    assert app.title == "Test API"
    assert app.version == "1.0"
    assert app.description == "Test Desc"
    assert app.contact == {
        "name": "Test",
        "email": "test@test.com",
        "url": "http://test.com",
    }
