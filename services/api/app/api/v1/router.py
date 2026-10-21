from fastapi import APIRouter

from app.api.v1.routes import health

api_v1_router = APIRouter()

# Mount sub-routers
api_v1_router.include_router(health.router, tags=["health"])
