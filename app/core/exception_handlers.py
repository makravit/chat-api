"""Custom exception handlers for the FastAPI application.

Provides handlers for:
- HTTPException (framework-level errors raised by routes/dependencies)
- Exception (catch-all for unexpected failures)
- Specific AppError subclasses (domain/service errors)
"""

from __future__ import annotations

from http import HTTPStatus

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, Response

from app.core.exceptions import (
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


def _build_json_response(status_code: int, code: str, detail: str) -> JSONResponse:
    """Create a JSONResponse with the project's standard error payload.

    Args:
        status_code: HTTP status code to return.
        code: Stable, machine-readable error code.
        detail: Human-readable error detail.

    Returns:
        A JSONResponse containing the standardized error schema.
    """
    return JSONResponse(
        status_code=status_code, content={"detail": detail, "code": code}
    )


def _build_no_content_response() -> Response:
    """Create an empty 204 No Content response."""
    return Response(status_code=204)


def _maybe_clear_refresh_cookie(response: Response, exc: Exception) -> None:
    """Delete the refresh cookie for credential/session-related failures.

    The cookie is cleared for InvalidCredentialsError and the two logout
    idempotency exceptions to avoid retaining stale session state on the client.
    """
    if isinstance(exc, _COOKIE_CLEAR_EXCS):
        response.delete_cookie(REFRESH_COOKIE_NAME, **_COOKIE_KW)


def _is_default_http_detail(status_code: int, detail: object) -> bool:
    """Return True if the provided detail equals the default phrase for the code.

    Starlette's HTTPException replaces ``None`` detail with the default HTTP
    status phrase (e.g., 401 -> "Unauthorized"). In those cases, we treat this
    as "no custom detail" and omit the detail from the JSON body to keep the
    payload compact and stable.
    """
    try:
        return str(detail) == HTTPStatus(status_code).phrase
    except ValueError:
        # Unknown/non-standard status code -> no default phrase known
        return False


async def email_already_registered_handler(
    request: Request, exc: Exception
) -> Response:
    """Return 409 Conflict for duplicate email registration attempts."""
    # FastAPI passes the specific subclass instance; accept Exception for typing.
    logger.warning(
        "AppError handled",
        exc_type=type(exc).__name__,
        status_code=409,
        detail=str(exc),
        path=_get_path(request),
    )
    return _build_json_response(409, "email_already_registered", str(exc))


async def invalid_credentials_handler(request: Request, exc: Exception) -> Response:
    """Return 401 Unauthorized for invalid credential scenarios.

    Also clears the refresh cookie to prevent clients from reusing a bad token.
    """
    logger.warning(
        "AppError handled",
        exc_type=type(exc).__name__,
        status_code=401,
        detail=str(exc),
        path=_get_path(request),
    )
    resp = _build_json_response(401, "invalid_credentials", str(exc))
    _maybe_clear_refresh_cookie(resp, exc)
    return resp


async def logout_no_session_handler(request: Request, exc: Exception) -> Response:
    """Return 204 No Content for idempotent logout with no active session.

    Clears the refresh cookie to ensure client state is reset.
    """
    logger.warning(
        "AppError handled",
        exc_type=type(exc).__name__,
        status_code=204,
        detail=str(exc),
        path=_get_path(request),
    )
    resp = _build_no_content_response()
    _maybe_clear_refresh_cookie(resp, exc)
    return resp


async def logout_operation_error_handler(request: Request, exc: Exception) -> Response:
    """Return 204 No Content for non-credential logout errors (idempotent).

    Operational issues during logout should not break idempotency; the client
    still receives a 204 and the refresh cookie is cleared.
    """
    logger.warning(
        "AppError handled",
        exc_type=type(exc).__name__,
        status_code=204,
        detail=str(exc),
        path=_get_path(request),
    )
    resp = _build_no_content_response()
    _maybe_clear_refresh_cookie(resp, exc)
    return resp


# Note: No separate generic AppError handler is registered at startup. The
# catch-all Exception handler is registered for runtime. The dispatcher above
# still returns 500 with detail for unit-test convenience.


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
        # Preserve response shape: include detail only when it's explicitly set
        # to something other than the default HTTP phrase that Starlette adds.
        if exc.detail is not None and not _is_default_http_detail(
            exc.status_code, exc.detail
        ):
            response = _build_json_response(
                exc.status_code, "http_error", str(exc.detail)
            )
        else:
            response = JSONResponse(
                status_code=exc.status_code, content={"code": "http_error"}
            )
        if exc.headers:
            response.headers.update(exc.headers)
        return response
    # Fallback if a non-HTTPException is routed here unexpectedly
    logger.error(
        "http_exception_handler received non-HTTPException",
        exc_type=type(exc).__name__,
        path=_get_path(request),
    )
    return _build_json_response(500, "internal_error", "Internal server error.")


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
    return _build_json_response(500, "internal_error", "Internal server error.")
