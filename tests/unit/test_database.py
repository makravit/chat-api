from contextlib import suppress

from app.core.database import get_db


def test_get_db_returns_session() -> None:
    gen = get_db()
    db = next(gen)
    try:
        assert db is not None
    finally:
        with suppress(StopIteration):
            next(gen)
