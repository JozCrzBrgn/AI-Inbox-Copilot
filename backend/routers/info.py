from fastapi import APIRouter, Request

from ..core.config import get_settings
from ..middleware.rate_limiter import limiter
from ..schemas.info import InfoResponse

cnf = get_settings()

router = APIRouter()

@router.get(
    "/",
    response_model=InfoResponse,
    summary="API information.",
    description="Basic API Information.",
    tags=["Information"],
)
@limiter.limit("5/minute")
async def root(request: Request):
    return InfoResponse(
        created_by=cnf.api_info.contact_name,
        description=cnf.api_info.description,
        version=cnf.api_info.version,
    )