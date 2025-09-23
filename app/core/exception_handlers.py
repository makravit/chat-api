"""Custom exception handlers for the FastAPI application.

Provides handlers for:
- AppError (domain/service errors)
- HTTPException (framework-level errors raised by routes/dependencies)
- Exception (catch-all for unexpected failures)
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, Response

from app.core.exceptions import (
    AppError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from app.core.logging import logger

# Duplicate cookie constants here to avoid import cycles with API layer
REFRESH_COOKIE_NAME = "refresh_token"
_COOKIE_KW = {"httponly": True, "secure": True, "samesite": "strict"}


async def app_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle AppError and map it to an appropriate HTTP response.

    Logs the error with structured context and returns a JSON body containing
    the error detail. Specific subclasses map to 401/409; otherwise 500.
    """
    # Map specific exceptions to status codes
    if isinstance(exc, EmailAlreadyRegisteredError):
        status_code = 409
        log_func = logger.warning
        code = "email_already_registered"
    elif isinstance(exc, InvalidCredentialsError):
        status_code = 401
        log_func = logger.warning
        code = "invalid_credentials"
    elif isinstance(exc, AppError):
        # Other AppError subclasses
        status_code = 500
        log_func = logger.error
        code = "app_error"
    else:
        status_code = 500
        log_func = logger.error
        code = "app_error"
    log_func(
        "AppError handled",
        exc_type=type(exc).__name__,
        status_code=status_code,
        detail=str(exc),
        path=str(getattr(request, "url", "unknown")),
    )
    response = JSONResponse(
        status_code=status_code,
        content={"detail": str(exc), "code": code},
    )
    # Proactively clear stale refresh cookie on credential/session failures.
    if isinstance(exc, InvalidCredentialsError):
        response.delete_cookie(REFRESH_COOKIE_NAME, **_COOKIE_KW)
    return response


async def http_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle HTTPException with structured logging and preserved headers.

    Args:
        request: The incoming request.
        exc: The ``HTTPException`` raised by a route/dependency.

    Returns:
        A JSON response mirroring the HTTP status and detail of the exception,
        while preserving any headers (e.g., WWW-Authenticate).
    """
    if isinstance(exc, HTTPException):
        logger.warning(
            "HTTPException handled",
            status_code=exc.status_code,
            detail=exc.detail,
            path=str(getattr(request, "url", "unknown")),
        )
        content = (
            {"detail": exc.detail, "code": "http_error"}
            if exc.detail is not None
            else {"code": "http_error"}
        )
        response = JSONResponse(status_code=exc.status_code, content=content)
        if exc.headers:
            for key, value in exc.headers.items():
                response.headers[key] = value
        return response
    # Fallback if a non-HTTPException is routed here unexpectedly
    logger.error(
        "http_exception_handler received non-HTTPException",
        exc_type=type(exc).__name__,
        path=str(getattr(request, "url", "unknown")),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error.", "code": "internal_error"},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    """Catch-all handler for unexpected exceptions.

    Logs the exception and returns a safe 500 response without leaking details.

    Args:
        request: The incoming request.
        exc: The unexpected exception.

    Returns:
        JSON response with a generic error message and HTTP 500 status code.
    """
    logger.exception(
        "Unhandled exception",
        exc_type=type(exc).__name__,
        path=str(getattr(request, "url", "unknown")),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error.", "code": "internal_error"},
    )
