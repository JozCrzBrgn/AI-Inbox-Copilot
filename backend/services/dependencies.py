from fastapi import Depends, Request

from .security import decode_access_token


def get_current_user(request: Request, username: str = Depends(decode_access_token)) -> str:
    """
    Dependency to obtain the currently authenticated user
    """

    # guardar usuario en request.state para rate limiter
    request.state.user = username

    return username