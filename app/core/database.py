
# Standard library imports
import contextlib
import typing

# Local application imports
from app.core.config import settings

# Third-party imports
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def get_engine():
    return create_engine(settings.DATABASE_URL)

def get_session_local():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

Base = declarative_base()

@contextlib.contextmanager
def get_db() -> typing.Generator:
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
