import hashlib
import secrets
from jose import jwt
from typing import Optional, Dict, Any
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_salt() -> str:
    return secrets.token_hex(16)


def hash_password(salt: str, password: str) -> str:  # noqa: ARG001
    """Return a bcrypt hash for new passwords; keep signature for callers.

    The salt parameter is ignored for new hashes but preserved for API
    compatibility.
    """
    return pwd_context.hash(password)


def verify_password(salt: str, stored_hash: str, password: str) -> bool:
    """Verify password against either bcrypt (preferred) or legacy sha256."""
    if not stored_hash:
        return False
    # Bcrypt hashes start with $2*
    if stored_hash.startswith("$2"):
        try:
            return pwd_context.verify(password, stored_hash)
        except Exception:  # noqa: BLE001
            return False
    # Legacy fallback: salted sha256
    if not salt:
        return False
    legacy = hashlib.sha256(
        (salt + password).encode("utf-8")
    ).hexdigest()
    return stored_hash == legacy


def create_jwt_token(payload: Dict[str, Any], secret: str) -> str:
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_jwt_token(token: str, secret: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(
            token, secret, algorithms=["HS256"]
        )  # type: ignore
    except Exception:  # noqa: BLE001
        return None
