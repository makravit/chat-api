"""Application entrypoint for the FastAPI Chat API.

Initializes the FastAPI app, registers routers and exception handlers, and
adds a middleware that sets common security headers.
"""

from fastapi import FastAPI, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.api import chat, health, metrics, users
from app.core.exception_handlers import (
    email_already_registered_handler,
    http_exception_handler,
    invalid_credentials_handler,
    logout_no_session_handler,
    logout_operation_error_handler,
    unhandled_exception_handler,
)
from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    LogoutNoSessionError,
    LogoutOperationError,
)

app = FastAPI(
    title="AI Chatbot API",
    description=("A REST API for user registration, authentication, and AI chat."),
)


# API versioning: business endpoints under /api/v1; health is unversioned
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(health.router, tags=["health"])
app.include_router(metrics.router, tags=["metrics"])

# Register global exception handlers (specific before generic)
#
# Rationale:
# - Specific domain handlers map to precise status codes and side effects
#   (e.g., refresh-cookie clearing on auth/logout).
# - The single catch-all Exception handler is the final safety net for
#   anything unclassified.
# - Handlers accept `Exception` as their second parameter to satisfy FastAPI's
#   `add_exception_handler` typing, even though they are registered for
#   specific subclasses at runtime.
app.add_exception_handler(EmailAlreadyRegisteredError, email_already_registered_handler)
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
app.add_exception_handler(LogoutNoSessionError, logout_no_session_handler)
app.add_exception_handler(LogoutOperationError, logout_operation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that adds a minimal set of security headers."""

    async def dispatch(
        self: "SecurityHeadersMiddleware",
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process the request, then set security headers on the response."""
        response: Response = await call_next(request)
        # Basic hardening headers; CSP kept minimal to avoid breaking
        # existing endpoints.
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )
        # Minimal CSP suitable for API. Adjust if serving HTML.
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)
