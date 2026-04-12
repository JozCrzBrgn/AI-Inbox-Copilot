from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_user_or_ip(request: Request) -> str:
    if hasattr(request.state, "user"):
        return str(request.state.user)
    return get_remote_address(request)

limiter = Limiter(key_func=get_user_or_ip)