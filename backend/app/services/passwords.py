"""Password hashing with hashlib.scrypt (docs/security.md). Stored form:
scrypt$<n>$<r>$<p>$<salt b64>$<hash b64>
"""

import base64
import hashlib
import hmac
import secrets

N, R, P = 2**14, 8, 1
SALT_BYTES = 16
KEY_BYTES = 64


def _derive(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=KEY_BYTES)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    key = _derive(password, salt, N, R, P)
    b64 = base64.b64encode
    return f"scrypt${N}${R}${P}${b64(salt).decode()}${b64(key).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, n, r, p, salt, key = stored.split("$")
    except ValueError:
        return False
    if scheme != "scrypt":
        return False
    expected = base64.b64decode(key)
    actual = _derive(password, base64.b64decode(salt), int(n), int(r), int(p))
    return hmac.compare_digest(actual, expected)


# Verified against when the username is unknown, so both paths cost the same.
DUMMY_HASH = hash_password(secrets.token_urlsafe(16))
