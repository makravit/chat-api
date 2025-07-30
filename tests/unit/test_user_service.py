import pytest
from app.services.user_service import register_user, authenticate_user
from app.schemas.user import UserRegister, UserLogin
from fastapi import HTTPException
from app.services.user_repository import UserRepository
from app.core.auth import hash_password

class DummySession:
    def __init__(self):
        self.users = {}
        self.committed = False
        self._id_counter = 1
    def query(self, model):
        class Query:
            def __init__(self, users):
                self.users = users
            def filter(self, cond):
                email = cond.right.value
                class Result:
                    def first(inner_self):
                        return self.users.get(email)
                return Result()
        return Query(self.users)
    def add(self, user):
        if not getattr(user, "id", None):
            user.id = self._id_counter
            self._id_counter += 1
        self.users[user.email] = user
    def commit(self):
        self.committed = True
    def refresh(self, user):
        pass

class DummyUser:
    def __init__(self, name, email, hashed_password):
        self.id = 1
        self.name = name
        self.email = email
        self.hashed_password = hashed_password

@pytest.fixture
def dummy_db():
    return DummySession()

@pytest.fixture
def repo(dummy_db):
    return UserRepository(dummy_db)

def test_register_user_success(dummy_db):
    user = UserRegister(name="Test", email="test@example.com", password="Password1!")
    result = register_user(user, dummy_db)
    assert result.email == user.email
    assert dummy_db.committed

def test_register_user_duplicate(dummy_db):
    user = UserRegister(name="Test", email="test@example.com", password="Password1!")
    register_user(user, dummy_db)
    with pytest.raises(HTTPException) as exc:
        register_user(user, dummy_db)
    assert exc.value.status_code == 400
    assert "already registered" in exc.value.detail

def test_authenticate_user_success(dummy_db):
    user = UserRegister(name="Test", email="test@example.com", password="Password1!")
    register_user(user, dummy_db)
    login = UserLogin(email="test@example.com", password="Password1!")
    result = authenticate_user(login, dummy_db)
    assert result.access_token

def test_authenticate_user_wrong_password(dummy_db):
    user = UserRegister(name="Test", email="test@example.com", password="Password1!")
    register_user(user, dummy_db)
    login = UserLogin(email="test@example.com", password="WrongPass1!")
    with pytest.raises(HTTPException) as exc:
        authenticate_user(login, dummy_db)
    assert exc.value.status_code == 401
    assert "incorrect" in exc.value.detail

def test_authenticate_user_not_found(dummy_db):
    login = UserLogin(email="notfound@example.com", password="Password1!")
    with pytest.raises(HTTPException) as exc:
        authenticate_user(login, dummy_db)
    assert exc.value.status_code == 401
