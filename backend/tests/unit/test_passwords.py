"""Password hashing (spec 0002, AC-8)."""

from app.services.passwords import hash_password, verify_password


def test_password_hash_is_not_plaintext_and_verifies() -> None:
    stored = hash_password("gizli-parola")

    assert "gizli-parola" not in stored
    assert stored.startswith("scrypt$")
    assert verify_password("gizli-parola", stored)
    assert not verify_password("gizli-parolA", stored)
    assert hash_password("gizli-parola") != stored  # a fresh salt every time
