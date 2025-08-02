
# Standard library imports

# Third-party imports
from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

# Local application imports

router = APIRouter()

@router.get("/metrics", summary="Prometheus metrics endpoint", tags=["metrics"])
def metrics():
    """
    Expose Prometheus metrics in text format for monitoring.
    Best practice: Only expose internally or protect with authentication if public.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
