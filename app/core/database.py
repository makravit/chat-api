"""Database engine and session management.

Provides helpers to create the SQLAlchemy engine, session factory, Declarative
Base, and a FastAPI dependency that yields a scoped Session.
"""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings


def get_engine() -> "Engine":
    """Create and return a SQLAlchemy Engine bound to the configured URL."""
    return create_engine(settings.DATABASE_URL)


def get_session_local() -> sessionmaker[Session]:
    """Return a configured sessionmaker bound to the application Engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


Base = declarative_base()


def get_db() -> Generator[Session]:
    """Yield a SQLAlchemy Session and ensure it's closed.

    This is a FastAPI dependency. It must be a generator (yield) and not be
    wrapped with @contextmanager so FastAPI receives the yielded Session
    instance directly.
    """
    db: Session = get_session_local()()
    try:
        yield db
    finally:
        db.close()
