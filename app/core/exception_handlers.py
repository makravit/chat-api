
# Standard library imports


# Third-party imports
from fastapi import Request
from fastapi.responses import JSONResponse, Response

# Local application imports
from app.core.exceptions import AppException, EmailAlreadyRegistered, InvalidCredentials
from app.core.logging import logger

async def app_exception_handler(request: Request, exc: AppException) -> Response:
    # Map specific exceptions to status codes
    if isinstance(exc, EmailAlreadyRegistered):
        status_code = 409
        log_func = logger.warning
    elif isinstance(exc, InvalidCredentials):
        status_code = 401
        log_func = logger.warning
    else:
        status_code = 500
        log_func = logger.error
    log_func(
        "AppException handled",
        exc_type=type(exc).__name__,
        status_code=status_code,
        detail=str(exc),
        path=str(getattr(request, 'url', 'unknown')),
    )
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
