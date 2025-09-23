"""Custom exception handlers for the FastAPI application.

Provides handlers for:
- AppError (domain/service errors)
- HTTPException (framework-level errors raised by routes/dependencies)
- Exception (catch-all for unexpected failures)
"""

from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, Response

from app.core.exceptions import (
    AppError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    LogoutNoSessionError,
    LogoutOperationError,
)
from app.core.logging import logger

# Duplicate cookie constants here to avoid import cycles with API layer
REFRESH_COOKIE_NAME = "refresh_token"
_COOKIE_KW = {"httponly": True, "secure": True, "samesite": "strict"}

# Exceptions that should proactively clear the refresh cookie on the response
_COOKIE_CLEAR_EXCS = (
    InvalidCredentialsError,
    LogoutOperationError,
    LogoutNoSessionError,
)


def _get_path(request: Request) -> str:
    """Return the request URL string for logging, or "unknown" if absent."""
    return str(getattr(request, "url", "unknown"))


async def app_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle AppError and map it to an appropriate HTTP response.

    Logs the error with structured context and returns a JSON body containing
    the error detail. Specific subclasses map to 401/409/204; otherwise 500.
    """
    path = _get_path(request)

    # Map specific exceptions to status codes (with special-case for logout idempotency)
    if isinstance(exc, EmailAlreadyRegisteredError):
        status_code = 409
        log_func = logger.warning
        code = "email_already_registered"
    elif isinstance(exc, InvalidCredentialsError):
        # Standard auth failures map to 401.
        status_code = 401
        log_func = logger.warning
        code = "invalid_credentials"
    elif isinstance(exc, LogoutNoSessionError):
        # Idempotent logout when no usable session/token
        status_code = 204
        log_func = logger.warning
        code = "logout_no_session"
    elif isinstance(exc, LogoutOperationError):
        # Non-credential failures during logout should be idempotent
        status_code = 204
        log_func = logger.warning
        code = "logout_operation_error"
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
        path=path,
    )
    # Build response; 204 must not include a body
    if status_code == 204:
        response: Response = Response(status_code=204)
    else:
        response = JSONResponse(
            status_code=status_code,
            content={"detail": str(exc), "code": code},
        )
    # Proactively clear stale refresh cookie on credential/session failures.
    if isinstance(exc, _COOKIE_CLEAR_EXCS):
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
            path=_get_path(request),
        )
        content = (
            {"detail": exc.detail, "code": "http_error"}
            if exc.detail is not None
            else {"code": "http_error"}
        )
        response = JSONResponse(status_code=exc.status_code, content=content)
        if exc.headers:
            response.headers.update(exc.headers)
        return response
    # Fallback if a non-HTTPException is routed here unexpectedly
    logger.error(
        "http_exception_handler received non-HTTPException",
        exc_type=type(exc).__name__,
        path=_get_path(request),
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
        path=_get_path(request),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error.", "code": "internal_error"},
    )
