
# Standard library imports
from unittest.mock import MagicMock

# Third-party imports

# Local application imports
from app.models.user import User
from app.services.user_repository import UserRepository

def make_db_with_users(users=None):
    db = MagicMock()
    db.users = users or []
    def query(model):
        query_mock = MagicMock()
        def filter(cond):
            email = cond.right.value
            result = next((u for u in db.users if u.email == email), None)
            first_mock = MagicMock(return_value=result)
            return MagicMock(first=first_mock)
        query_mock.filter.side_effect = filter
        return query_mock
    db.query.side_effect = query
    db.add.side_effect = lambda user: db.users.append(user)
    db.commit.side_effect = lambda: setattr(db, 'committed', True)
    db.refresh.side_effect = lambda user: None
    db.committed = False
    return db

def test_get_by_email_found():
    user = User(id=1, name="Test", email="test@example.com", hashed_password="x")
    db = make_db_with_users([user])
    repo = UserRepository(db)
    result = repo.get_by_email("test@example.com")
    assert result is user

def test_get_by_email_not_found():
    db = make_db_with_users([])
    repo = UserRepository(db)
    result = repo.get_by_email("notfound@example.com")
    assert result is None

def test_create_user():
    db = make_db_with_users([])
    repo = UserRepository(db)
    user = repo.create(name="Test", email="test@example.com", hashed_password="x")
    assert user in db.users
    assert db.committed
    assert user.name == "Test"
    assert user.email == "test@example.com"
    assert user.hashed_password == "x"
