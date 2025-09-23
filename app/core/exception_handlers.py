"""Custom exception handlers for the FastAPI application."""

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from app.core.exceptions import (
    AppError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from app.core.logging import logger


async def app_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle AppError and map it to an appropriate HTTP response.

    Logs the error with structured context and returns a JSON body containing
    the error detail. Specific subclasses map to 401/409; otherwise 500.
    """
    # Map specific exceptions to status codes
    if isinstance(exc, EmailAlreadyRegisteredError):
        status_code = 409
        log_func = logger.warning
    elif isinstance(exc, InvalidCredentialsError):
        status_code = 401
        log_func = logger.warning
    elif isinstance(exc, AppError):
        # Other AppError subclasses
        status_code = 500
        log_func = logger.error
    else:
        status_code = 500
        log_func = logger.error
    log_func(
        "AppError handled",
        exc_type=type(exc).__name__,
        status_code=status_code,
        detail=str(exc),
        path=str(getattr(request, "url", "unknown")),
    )
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
