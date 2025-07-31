
# Standard library imports

# Third-party imports
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# Local application imports
from app.core.logging import logger
from app.core.database import get_db

router = APIRouter()


@router.get("/live", tags=["Health"])
def liveness_probe():
    """Liveness probe: returns 200 if app is running."""
    return {"status": "alive"}

@router.get("/ready", tags=["Health"])
def readiness_probe():
    """Readiness probe: returns 200 if DB is up, 503 if not."""
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except SQLAlchemyError as e:
        logger.error("Readiness check DB failure", error=str(e))
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "not ready"})

@router.get("/health", tags=["Health"])
def health_check():
    """Detailed health check: returns app and DB status."""
    db_status = "ok"
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        db_status = "down"
        logger.error("Health check DB failure", error=str(e))
    logger.info("Health check", db=db_status)
    return {"status": "ok" if db_status == "ok" else "error", "db": db_status}
