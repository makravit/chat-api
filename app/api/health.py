
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

@router.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for readiness/liveness probes, including DB connectivity."""
    db_status = "ok"
    http_status = status.HTTP_200_OK
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        db_status = "down"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        logger.error("Health check DB failure", error=str(e))
    logger.info("Health check", db=db_status)
    return JSONResponse(status_code=http_status, content={"status": "ok" if db_status == "ok" else "error", "db": db_status})
