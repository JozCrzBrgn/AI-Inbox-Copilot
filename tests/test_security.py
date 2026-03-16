from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from backend.core.config import get_settings
from backend.main import app
from backend.services.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_password,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_create_access_token_basic():
    """Create basic token"""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expiration():
    """Create token with custom expiration"""
    data = {"sub": "testuser"}
    expires = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=expires)
    
    assert token is not None


def test_decode_valid_token():
    """Decode valid token"""
    cnf = get_settings()
    username = "testuser"
    token = create_access_token({"sub": username})
    
    # Manually decode for testing
    payload = jwt.decode(token, cnf.security.jwt_secret, algorithms=[cnf.security.algorithm])
    
    assert payload["sub"] == username
    assert "exp" in payload


def test_decode_invalid_token():
    """Attempt to decode invalid token"""
    cnf = get_settings()
    invalid_token = "invalid.token.string"
    
    with pytest.raises(Exception):
        jwt.decode(invalid_token, cnf.security.jwt_secret, algorithms=[cnf.security.algorithm])


def test_password_hash_generation():
    """Generate password hash"""
    password = "mysecretpassword"
    hashed = get_password_hash(password)
    
    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed != password
    assert len(hashed) > 0


def test_password_verification_correct():
    """Verify correct password"""
    password = "mysecretpassword"
    hashed = get_password_hash(password)
    
    result = verify_password(password, hashed)
    assert result is True


def test_password_verification_incorrect():
    """Check for incorrect password"""
    password = "mysecretpassword"
    wrong_password = "wrongpassword"
    hashed = get_password_hash(password)
    
    result = verify_password(wrong_password, hashed)
    assert result is False


def test_different_passwords_different_hashes():
    """Different passwords produce different hashes"""
    hash1 = get_password_hash("password123")
    hash2 = get_password_hash("password456")
    
    assert hash1 != hash2


def test_authenticate_valid_user():
    """Authenticate valid user"""
    cnf = get_settings()
    
    username = cnf.security.auth_username
    password = cnf.security.auth_password
    
    result = authenticate_user(username, password)
    
    assert result is not False
    assert result["username"] == username


def test_authenticate_wrong_password():
    """Authenticating with incorrect password"""
    cnf = get_settings()
    
    username = cnf.security.auth_username
    wrong_password = "wrongpassword"
    
    result = authenticate_user(username, wrong_password)
    assert result is False


def test_authenticate_nonexistent_user():
    """Authenticating a user that does not exist"""
    result = authenticate_user("nonexistentuser", "anypassword")
    assert result is False


def test_authenticate_empty_username():
    """Authenticate with an empty username"""
    result = authenticate_user("", "anypassword")
    assert result is False


def test_authenticate_empty_password():
    """Authenticate with an empty password"""
    cnf = get_settings()
    result = authenticate_user(cnf.security.auth_username, "")
    assert result is False


def test_create_and_decode_token_integration():
    """Create a token and decode it"""
    cnf = get_settings()
    username = "integration_test_user"

    token = create_access_token({"sub": username})
    
    decoded = jwt.decode(token, cnf.security.jwt_secret, algorithms=[cnf.security.algorithm])
    
    assert decoded["sub"] == username
    assert "exp" in decoded


def test_token_has_expiration():
    """Verify that the token has an expiration date"""
    cnf = get_settings()
    token = create_access_token({"sub": "testuser"})
    
    decoded = jwt.decode(token, cnf.security.jwt_secret, algorithms=[cnf.security.algorithm])
    
    assert "exp" in decoded
    assert isinstance(decoded["exp"], int)


def test_create_token_with_empty_data():
    """Create token with empty data"""
    token = create_access_token({})
    assert token is not None


def test_create_token_with_none_data():
    """Create token with None (should fail)"""
    with pytest.raises(Exception):
        create_access_token(None)


def test_token_with_zero_expiration():
    """Token with 0 minute expiration"""
    cnf = get_settings()
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=0))
    
    decoded = jwt.decode(token, cnf.security.jwt_secret, algorithms=[cnf.security.algorithm])
    assert "exp" in decoded


def test_verify_password_with_invalid_hash():
    """Verify password with invalid hash"""
    invalid_hash = "not_a_valid_hash"
    
    with pytest.raises(Exception):
        verify_password("anypassword", invalid_hash)