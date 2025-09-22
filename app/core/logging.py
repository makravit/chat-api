"""Structured logging setup and helpers."""

import structlog

from app.core.config import settings

# Map string log level to structlog/stdlib level
_LOG_LEVELS = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0,
}
log_level = _LOG_LEVELS.get(settings.LOG_LEVEL.upper(), _LOG_LEVELS["INFO"])

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(log_level),
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def mask_token(token: str | None) -> str | None:
    """Return a short, non-sensitive fingerprint for a secret token.

    Examples:
      - None -> None
      - "abcd1234" -> "********" (fully masked if very short)
      - "abcde12345" -> "abcd...2345"
    """
    if token is None:
        return None
    try:
        length = len(token)
    except TypeError:
        return "***"
    if length <= 8:
        return "*" * length
    return f"{token[:4]}...{token[-4:]}"
