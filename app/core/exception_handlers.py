from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException, EmailAlreadyRegistered, InvalidCredentials

async def app_exception_handler(request: Request, exc: AppException):
    # Map specific exceptions to status codes
    if isinstance(exc, EmailAlreadyRegistered):
        status_code = 409
    elif isinstance(exc, InvalidCredentials):
        status_code = 401
    else:
        status_code = 400
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
