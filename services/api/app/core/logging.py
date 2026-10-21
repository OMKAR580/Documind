import logging
import re
import sys


def sanitize_sensitive_url(url: str | None) -> str:
    """Masks credentials in database and redis URLs for safe logging."""
    if not url:
        return ""
    # Matches ://user:password@ pattern and masks password
    return re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)


def setup_logging(log_level: str = "INFO", debug: bool = False) -> None:
    """Configures structured, sanitized logging for the API service."""
    effective_level = logging.DEBUG if debug else getattr(logging, log_level.upper(), logging.INFO)

    log_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=effective_level,
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
        force=True,
    )

    # Suppress verbose noisy third-party loggers unless debugging
    if not debug:
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("alembic").setLevel(logging.INFO)
