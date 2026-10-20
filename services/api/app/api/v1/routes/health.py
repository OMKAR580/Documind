from datetime import UTC, datetime

from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.core.database import check_database_connection

router = APIRouter()


@router.get("/health", summary="Service Liveness Check")
@router.get("/health/live", summary="Kubernetes Liveness Probe")
async def liveness_check():
    """
    Process liveness check.
    Confirms the FastAPI application process is alive and receiving traffic.
    Does NOT imply downstream dependencies (DB/Redis) are healthy.
    """
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready", summary="Service Readiness Probe")
async def readiness_check(response: Response):
    """
    Service readiness check.
    Validates connectivity to essential backing dependencies like PostgreSQL.
    Returns HTTP 200 if healthy and ready to serve traffic.
    Returns HTTP 503 if backing dependencies are unavailable.
    """
    db_ok, db_err = check_database_connection()

    components = {
        "database": {
            "status": "healthy" if db_ok else "unhealthy",
            "details": "PostgreSQL reachable" if db_ok else f"PostgreSQL unavailable: {db_err}",
        }
    }

    is_ready = db_ok
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "unhealthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(UTC).isoformat(),
        "components": components,
    }
