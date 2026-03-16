from fastapi import APIRouter, Depends, Request

from ..middleware.rate_limiter import limiter
from ..schemas.email_analizer import EmailAnalizerResponse
from ..services.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/production",
    response_model=EmailAnalizerResponse,
    summary="modificar summary",
    description="modificar descriptipon",
    tags=["Email analyzer"],
)
@limiter.limit("5/minute")
async def production(
    request: Request,
    username: str = Depends(get_current_user),
) -> EmailAnalizerResponse:
    """
    """
    
    # Construir respuesta con metadata
    return EmailAnalizerResponse(
        success=True,
        message="Todo ok"
    )
