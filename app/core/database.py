

import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


import typing

@contextlib.contextmanager
def get_db() -> typing.Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
