from unittest.mock import MagicMock

import pytest
from fastapi import Depends, Request

from backend.services.dependencies import get_current_user


def test_get_current_user_returns_username():
    """Returns the username correctly"""
    # Create a mock request
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock()
    
    # Simulate that decode_access_token returns a username
    expected_username = "testuser"
    
    # Call the function with the simulated username
    # Note: Since it has Depends, we can call it directly in testing.
    result = get_current_user(request=mock_request, username=expected_username)
    
    assert result == expected_username
    assert isinstance(result, str)


def test_get_current_user_in_endpoint(app_client):
    """Test with simulated endpoint"""
    
    # Create a temporary test endpoint
    from fastapi import APIRouter
    
    test_router = APIRouter()
    
    @test_router.get("/test-protected")
    async def protected_endpoint(current_user: str = Depends(get_current_user)):
        return {"user": current_user}
    
    # Set up the temporary router
    app_client.app.include_router(test_router)
    
    # Create token for authentication
    from backend.services.security import create_access_token
    token = create_access_token({"sub": "testuser"})
    
    # Make request with token
    response = app_client.get(
        "/test-protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "testuser"


def test_get_current_user_no_token(app_client):
    """Call a protected endpoint without a token"""
    from fastapi import APIRouter
    
    test_router = APIRouter()
    
    @test_router.get("/test-protected")
    async def protected_endpoint(current_user: str = Depends(get_current_user)):
        return {"user": current_user}
    
    app_client.app.include_router(test_router)
    
    # Make request without token
    response = app_client.get("/test-protected")
    
    # It should return 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_get_current_user_invalid_token(app_client):
    """Use invalid token"""
    from fastapi import APIRouter
    
    test_router = APIRouter()
    
    @test_router.get("/test-protected")
    async def protected_endpoint(current_user: str = Depends(get_current_user)):
        return {"user": current_user}
    
    app_client.app.include_router(test_router)
    
    # Make request with invalid token
    response = app_client.get(
        "/test-protected",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    
    assert response.status_code == 401


@pytest.mark.parametrize("username,expected", [
    ("admin", "admin"),
    ("user123", "user123"),
    ("test@example.com", "test@example.com"),
    ("", ""),  # Empty username
])
def test_get_current_user_parametrized(username, expected):
    """Parameterized test with different usernames"""
    # Create a mock request
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock()

    result = get_current_user(request=mock_request, username=username)
    assert result == expected


def test_get_current_user_return_type():
    """Verify that it always returns a string"""
    # Create a mock request
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock()

    result = get_current_user(request=mock_request, username="testuser")
    assert isinstance(result, str)
    
    result = get_current_user(request=mock_request, username="")
    assert isinstance(result, str)


def test_get_current_user_composition():
    """composition with other dependencies"""
    
    def process_user(current_user: str = Depends(get_current_user)):
        return f"Processed: {current_user}"
    
    # Simular la inyección
    result = process_user(current_user="testuser")
    assert result == "Processed: testuser"