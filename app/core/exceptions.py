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
