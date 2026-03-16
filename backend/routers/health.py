from datetime import datetime

from fastapi import APIRouter, Request

from ..core.config import get_settings
from ..middleware.rate_limiter import limiter
from ..schemas.health import HealthResponse

cnf = get_settings()

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Endpoint to verify API health.",
    tags=["Information"],
)
@limiter.limit("5/minute")
async def health_check(request: Request) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=cnf.api_info.version,
    )
