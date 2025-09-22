"""Prometheus metrics endpoint.

Exposes metrics in the Prometheus text exposition format and protects the
endpoint with Basic Authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.auth import basic_auth_guard
from app.core.config import settings

router = APIRouter()


@router.get("/metrics", summary="Prometheus metrics endpoint", tags=["metrics"])
def metrics(
    _: Annotated[
        object,
        Depends(basic_auth_guard(settings.METRICS_USER, settings.METRICS_PASS)),
    ],
) -> Response:
    """Expose Prometheus metrics for monitoring.

    Returns metrics in the Prometheus text exposition format. Access is
    protected with Basic Authentication using credentials from environment
    variables.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
