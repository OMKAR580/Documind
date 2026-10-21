import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_db_engine(database_url: str | None = None) -> Engine:
    """Creates a configured SQLAlchemy Engine instance."""
    url = database_url or settings.sync_database_url
    engine_kwargs: dict = {
        "echo": settings.DEBUG,
        "pool_pre_ping": True,
    }

    # Add pool tuning arguments for server-based databases (PostgreSQL)
    if not url.startswith("sqlite"):
        engine_kwargs.update(
            {
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
                "pool_recycle": settings.DB_POOL_RECYCLE,
            }
        )

    return create_engine(url, **engine_kwargs)


# Global engine and sessionmaker
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding database sessions with guaranteed cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> tuple[bool, str | None]:
    """
    Checks whether the database is reachable and responding.
    Returns (is_connected, sanitized_error_summary).
    Never throws unhandled exceptions or leaks sensitive credentials.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:
        logger.error(
            "Database connectivity check failed: %s (target: %s)",
            exc,
            settings.sanitized_database_url,
        )
        return False, "Database connection unavailable or unhealthy"
