"""
Custom exception hierarchy for application/service errors.
"""

class AppException(Exception):
    """Base exception for all application/service errors."""
    def __init__(self, message: str = "An application error occurred."):
        super().__init__(message)

class EmailAlreadyRegistered(AppException):
    """Exception raised when attempting to register an email that already exists."""
    def __init__(self, message: str = "Email is already registered."):
        super().__init__(message)

class InvalidCredentials(AppException):
    """Exception raised for invalid login credentials."""
    def __init__(self, message: str = "Email or password incorrect."):
        super().__init__(message)
