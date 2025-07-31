from app.models.user import User

def test_user_model_fields():
    user = User(id=1, name="Test User", email="test@example.com", hashed_password="hashed")
    assert user.id == 1
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed"
    # Check __tablename__ and column properties
    assert User.__tablename__ == "users"
    assert hasattr(User, "id")
    assert hasattr(User, "name")
    assert hasattr(User, "email")
    assert hasattr(User, "hashed_password")
