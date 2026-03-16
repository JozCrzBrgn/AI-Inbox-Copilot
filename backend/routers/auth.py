from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas.auth import TokenResponse
from ..services.security import authenticate_user, create_access_token

router = APIRouter()


@router.post(
    "/token",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="Get JWT token",
    description="Generates a JWT token for user authentication.",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password.",
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return TokenResponse(access_token=access_token, token_type="bearer")
