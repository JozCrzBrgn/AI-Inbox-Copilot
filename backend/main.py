from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .core.config import get_settings
from .middleware.rate_limiter import limiter
from .routers import auth, email_analizer, health, info

cnf = get_settings()


# FastAPI Initialization
app = FastAPI(
    title=cnf.api_info.name,
    description=cnf.api_info.description,
    version=cnf.api_info.version,
    contact={
        "name": cnf.api_info.contact_name,
        "email": cnf.api_info.contact_email,
        "url": cnf.api_info.contact_url,
    },
    license_info={"name": cnf.api_info.license, "url": cnf.api_info.license_url},
    openapi_tags=[
        {"name": "Authentication", "description": "Authentication and JWT tokens"},
        {"name": "Information", "description": "Basic API Information"},
        {"name": "Email analyzer", "description": "API to automatically analyze emails and help Customer Service (CS) teams prioritize and respond faster"},
    ]
)

# Configure rate limiter
app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cnf.cors.cors_allow_origins,
    allow_methods=cnf.cors.cors_allow_methods,
    allow_headers=cnf.cors.cors_allow_headers,
)

# Custom handler for rate limiting
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Request limit exceeded. Please try again later.",
            "path": str(request.url),
        },
        headers={"Retry-After": "60"}
    )


# Include routers
app.include_router(health.router, tags=["Information"])
app.include_router(info.router, tags=["Information"])
app.include_router(auth.router, tags=["Authentication"])
app.include_router(email_analizer.router, tags=["Email analyzer"], prefix="/v1")

