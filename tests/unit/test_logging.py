from types import SimpleNamespace

from app.core.logging import mask_token


def test_mask_token_none() -> None:
    assert mask_token(None) is None


def test_mask_token_short_full_mask() -> None:
    # length <= 8 should be fully masked
    assert mask_token("abcd1234") == "********"


def test_mask_token_long_fingerprint() -> None:
    tok = "abcdefghijklmnop"  # 16 chars
    assert mask_token(tok) == "abcd...mnop"


def test_mask_token_non_sized_returns_stars() -> None:
    def _len_raises() -> int:
        msg = "nope"
        raise RuntimeError(msg)

    obj = SimpleNamespace(__len__=_len_raises)
    assert mask_token(obj) == "***"
