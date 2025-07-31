
# Standard library imports
import contextlib
import typing

# Third-party imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Local application imports
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextlib.contextmanager
def get_db() -> typing.Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
