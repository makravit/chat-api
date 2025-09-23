"""Custom exception hierarchy for application/service errors."""


class AppError(Exception):
    """Base error for all application/service failures."""

    def __init__(
        self: "AppError",
        message: str = "An application error occurred.",
    ) -> None:
        """Initialize the base application error with a message.

        Args:
            message: Human-readable description of the error.
        """
        super().__init__(message)


class EmailAlreadyRegisteredError(AppError):
    """Raised when attempting to register an email that already exists."""

    def __init__(
        self: "EmailAlreadyRegisteredError",
        message: str = "Email is already registered.",
    ) -> None:
        """Create an EmailAlreadyRegisteredError.

        Args:
            message: Optional override for the default message.
        """
        super().__init__(message)


class InvalidCredentialsError(AppError):
    """Raised for invalid login credentials or invalid/expired session tokens."""

    def __init__(
        self: "InvalidCredentialsError",
        message: str = "Email or password incorrect.",
    ) -> None:
        """Create an InvalidCredentialsError.

        Args:
            message: Optional override for the default message.
        """
        super().__init__(message)


class LogoutOperationError(AppError):
    """Raised when a logout operation fails unexpectedly.

    Intended for the service layer to signal non-credential-related failures
    (e.g., database errors) so that the API can treat logout as idempotent
    without catching broad exceptions.
    """

    def __init__(
        self: "LogoutOperationError",
        message: str = "Logout operation failed.",
    ) -> None:
        """Initialize a LogoutOperationError with an optional message.

        Args:
            message: Human-readable description of the failure.
        """
        super().__init__(message)


class LogoutNoSessionError(AppError):
    """Raised when a logout request has no usable session/token.

    This signals idempotent logout behavior: the API should respond with 204
    No Content and clear the refresh cookie, without treating it as an error.
    """

    def __init__(
        self: "LogoutNoSessionError",
        message: str = "No active session or already logged out.",
    ) -> None:
        """Initialize a LogoutNoSessionError with an optional message.

        Args:
            message: Human-readable description of the condition.
        """
        super().__init__(message)
