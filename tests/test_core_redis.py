import pytest
from pydantic import ValidationError

from backend.core.config import RedisSettings


def test_valid_settings():
    settings = RedisSettings(
        host="localhost",
        port=6379,
        password="secret",
        db=0,
    )

    assert settings.host == "localhost"
    assert settings.port == 6379
    assert settings.password == "secret"
    assert settings.db == 0


def test_invalid_port_low():
    with pytest.raises(ValidationError) as exc:
        RedisSettings(
            host="localhost",
            port=0,
            password="secret",
        )

    assert "port must be between 1 and 65535" in str(exc.value)


def test_invalid_port_high():
    with pytest.raises(ValidationError) as exc:
        RedisSettings(
            host="localhost",
            port=70000,
            password="secret",
        )

    assert "port must be between 1 and 65535" in str(exc.value)


def test_invalid_db_low():
    with pytest.raises(ValidationError) as exc:
        RedisSettings(
            host="localhost",
            port=6379,
            password="secret",
            db=-1,
        )

    assert "db must be between 0 and 15" in str(exc.value)


def test_invalid_db_high():
    with pytest.raises(ValidationError) as exc:
        RedisSettings(
            host="localhost",
            port=6379,
            password="secret",
            db=20,
        )

    assert "db must be between 0 and 15" in str(exc.value)


def test_default_db_value():
    settings = RedisSettings(
        host="localhost",
        port=6379,
        password="secret",
    )

    assert settings.db == 0


def test_env_variables(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "127.0.0.1")
    monkeypatch.setenv("REDIS_PORT", "6380")
    monkeypatch.setenv("REDIS_PASSWORD", "env-secret")
    monkeypatch.setenv("REDIS_DB", "2")

    settings = RedisSettings()

    assert settings.host == "127.0.0.1"
    assert settings.port == 6380
    assert settings.password == "env-secret"
    assert settings.db == 2
