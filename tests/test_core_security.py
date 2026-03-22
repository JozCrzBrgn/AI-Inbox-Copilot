import pytest

from backend.core.security import SecuritySettings


def test_jwt_secret_too_short():
    with pytest.raises(ValueError):
        SecuritySettings(
            jwt_secret="short",
            algorithm="HS256",
            auth_username="admin",
            auth_password="password"
        )


def test_invalid_algorithm():
    with pytest.raises(ValueError):
        SecuritySettings(
            jwt_secret="a" * 32,
            algorithm="INVALID",
            auth_username="admin",
            auth_password="password"
        )


