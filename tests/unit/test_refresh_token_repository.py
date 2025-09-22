from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.models.refresh_token import RefreshToken
from app.repositories.refresh_token_repository import RefreshTokenRepository
from tests.utils import (
    join_parts,
    make_db_commit_mock,
    make_db_query_all,
    make_db_query_first,
)


def test_add_token_naive_datetime() -> None:
    db = make_db_commit_mock()
    repo = RefreshTokenRepository(db)
    naive_dt = datetime.now(UTC).replace(tzinfo=None)
    repo.add_token(1, join_parts("token"), naive_dt)
    db.add.assert_called_once()
    db.assert_committed_once()
    added_obj = db.add.call_args[0][0]
    assert isinstance(added_obj, RefreshToken)
    assert added_obj.expires_at.tzinfo is not None


def test_get_valid_token_none() -> None:
    db = make_db_query_first(None)
    repo = RefreshTokenRepository(db)
    assert repo.get_valid_token(join_parts("no-token")) is None


def test_get_valid_tokens_none() -> None:
    db = make_db_query_all([])
    repo = RefreshTokenRepository(db)
    assert repo.get_valid_tokens(123) == []


def test_get_valid_token_found() -> None:
    token_obj = RefreshToken(
        id=1,
        user_id=2,
        token=join_parts("tok-123"),
        expires_at=None,
        revoked=False,
        created_at=None,
    )
    db = make_db_query_first(token_obj)
    repo = RefreshTokenRepository(db)
    result = repo.get_valid_token(join_parts("tok-123"))
    assert result is token_obj


def test_get_valid_tokens_found() -> None:
    token_obj1 = RefreshToken(
        id=1,
        user_id=2,
        token=join_parts("tok-123"),
        expires_at=None,
        revoked=False,
        created_at=None,
    )
    token_obj2 = RefreshToken(
        id=2,
        user_id=2,
        token=join_parts("tok-456"),
        expires_at=None,
        revoked=False,
        created_at=None,
    )
    db = make_db_query_all([token_obj1, token_obj2])
    repo = RefreshTokenRepository(db)
    result = repo.get_valid_tokens(2)
    assert result == [token_obj1, token_obj2]


def test_revoke_token_updates_and_commits() -> None:
    db = make_db_commit_mock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    query_mock.filter.return_value = filter_mock
    db.query.return_value = query_mock

    repo = RefreshTokenRepository(db)
    repo.revoke_token(join_parts("t-123"))

    db.query.assert_called_once_with(RefreshToken)
    filter_mock.update.assert_called_once_with({"revoked": True})
    db.assert_committed_once()


def test_revoke_all_tokens_updates_and_commits() -> None:
    db = make_db_commit_mock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    query_mock.filter.return_value = filter_mock
    db.query.return_value = query_mock

    repo = RefreshTokenRepository(db)
    repo.revoke_all_tokens(42)

    db.query.assert_called_once_with(RefreshToken)
    filter_mock.update.assert_called_once_with({"revoked": True})
    db.assert_committed_once()
