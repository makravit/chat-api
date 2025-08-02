# Standard library imports

# Third-party imports
from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.auth import basic_auth_guard

# Local application imports
from app.core.config import settings

# Local application imports


router = APIRouter()

@router.get("/metrics", summary="Prometheus metrics endpoint", tags=["metrics"])
def metrics(credentials=Depends(basic_auth_guard(settings.METRICS_USER, settings.METRICS_PASS))):
    """
    Expose Prometheus metrics in text format for monitoring.
    Protected with Basic Authentication using credentials from environment variables.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
