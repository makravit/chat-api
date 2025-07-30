import pytest
from app.core.database import get_db

def test_get_db_returns_session():
    with get_db() as db:
        assert db is not None
