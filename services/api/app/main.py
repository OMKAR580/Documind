from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import health
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered multimodal document intelligence platform API",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(
    health.router,
    prefix=settings.API_V1_STR,
    tags=["health"],
)


@app.get("/", summary="Root API Information")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/api/docs",
        "health_url": f"{settings.API_V1_STR}/health",
    }
