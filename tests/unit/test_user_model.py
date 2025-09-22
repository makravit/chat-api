from app.models.user import User
from tests.utils import join_parts


def test_user_model_fields() -> None:
    user = User(
        id=1,
        name="Test User",
        email="test@example.com",
        hashed_password=join_parts("hashed"),
    )
    assert user.id == 1
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.hashed_password == join_parts("hashed")
    # Check __tablename__ and column properties
    assert User.__tablename__ == "users"
    assert hasattr(User, "id")
    assert hasattr(User, "name")
    assert hasattr(User, "email")
    assert hasattr(User, "hashed_password")
