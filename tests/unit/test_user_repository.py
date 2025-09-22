from unittest.mock import MagicMock

from app.models.user import User
from app.services.user_repository import UserRepository
from tests.utils import join_parts


def test_user_repository_init() -> None:
    db = MagicMock()
    repo = UserRepository(db)
    assert repo.db is db


def make_db_with_users(users: list[User] | None = None) -> MagicMock:
    db: MagicMock = MagicMock()
    db.users = users or []

    def query(_model: object) -> MagicMock:
        query_mock: MagicMock = MagicMock()

        def _filter(cond: object) -> MagicMock:
            # Simulate SQLAlchemy == comparator with .right.value
            email = getattr(getattr(cond, "right", object()), "value", None)
            result = next((u for u in db.users if u.email == email), None)
            first_mock: MagicMock = MagicMock(return_value=result)
            return MagicMock(first=first_mock)

        query_mock.filter.side_effect = _filter
        return query_mock

    db.query.side_effect = query
    db.add.side_effect = lambda _user: db.users.append(_user)
    db.commit.side_effect = lambda: setattr(db, "committed", True)
    db.refresh.side_effect = lambda _user: None
    db.committed = False
    return db


def test_get_by_email_found() -> None:
    user = User(
        id=1,
        name="Test",
        email="test@example.com",
        hashed_password=join_parts("x"),
    )
    db = make_db_with_users([user])
    repo = UserRepository(db)
    result = repo.get_by_email("test@example.com")
    assert result is user


def test_get_by_email_not_found() -> None:
    db = make_db_with_users([])
    repo = UserRepository(db)
    result = repo.get_by_email("notfound@example.com")
    assert result is None


def test_create_user() -> None:
    db = make_db_with_users([])
    repo = UserRepository(db)
    user = repo.create(
        name="Test",
        email="test@example.com",
        hashed_password=join_parts("x"),
    )
    assert user in db.users
    assert db.committed
    assert user.name == "Test"
    assert user.email == "test@example.com"
    assert user.hashed_password == join_parts("x")
