from datetime import UTC, datetime

from fastapi import APIRouter, Response, status
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.database import check_database_connection
from app.schemas.common import ComponentHealth, LivenessResponse, ReadinessResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=LivenessResponse,
    summary="Service Liveness Check",
)
@router.get(
    "/health/live",
    response_model=LivenessResponse,
    summary="Kubernetes Liveness Probe",
)
async def liveness_check() -> LivenessResponse:
    """
    Process liveness check.
    Confirms the FastAPI application process is alive and receiving traffic.
    Does NOT imply downstream dependencies (DB/Redis) are healthy.
    """
    return LivenessResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={
        200: {
            "model": ReadinessResponse,
            "description": "All critical backing dependencies are healthy",
        },
        503: {
            "model": ReadinessResponse,
            "description": "One or more critical backing dependencies are unavailable",
        },
    },
    summary="Service Readiness Probe",
)
async def readiness_check(response: Response) -> ReadinessResponse:
    """
    Service readiness check.
    Validates connectivity to essential backing dependencies like PostgreSQL.
    Runs blocking connection checks in a worker threadpool to avoid stalling the async event loop.
    Returns HTTP 200 if healthy and ready to serve traffic.
    Returns HTTP 503 if backing dependencies are unavailable, without leaking secrets.
    """
    db_ok, _ = await run_in_threadpool(check_database_connection)

    components = {
        "database": ComponentHealth(
            status="healthy" if db_ok else "unhealthy",
            details="PostgreSQL reachable" if db_ok else "PostgreSQL connection unavailable",
        )
    }

    is_ready = db_ok
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if is_ready else "unhealthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp=datetime.now(UTC).isoformat(),
        components=components,
    )
