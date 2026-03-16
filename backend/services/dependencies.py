from fastapi import Depends

from .security import decode_access_token


def get_current_user(username: str = Depends(decode_access_token)) -> str:
    """
    Dependency to obtain the currently authenticated user
    Args:
    username (str): Username obtained from the decoded JWT token
    """
    return username