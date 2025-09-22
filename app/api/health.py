"""Health and readiness probes.

Exposes liveness, readiness, and health endpoints used by orchestrators and
monitoring systems.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import Response

from app.core.database import get_session_local
from app.core.logging import logger

router = APIRouter()


@router.get("/live", tags=["Health"])
def liveness_probe() -> dict[str, str]:
    """Liveness probe: returns 200 if app is running."""
    return {"status": "alive"}


@router.get("/ready", tags=["Health"])
def readiness_probe() -> Response:
    """Readiness probe: returns 200 if DB is up, 503 if not."""
    try:
        db = get_session_local()()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except SQLAlchemyError as e:
        logger.error("Readiness check DB failure", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready"},
        )
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ready"})


@router.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Detailed health check: returns app and DB status."""
    db_status = "ok"
    try:
        db = get_session_local()()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except SQLAlchemyError as e:
        db_status = "down"
        logger.error("Health check DB failure", error=str(e))
    logger.info("Health check", db=db_status)
    return {"status": "ok" if db_status == "ok" else "error", "db": db_status}
