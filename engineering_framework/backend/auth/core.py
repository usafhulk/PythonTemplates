"""Auth Core."""
import base64
import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, Optional

from .interfaces import AuthToken, Authenticator, Credentials

logger = logging.getLogger(__name__)


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    return base64.urlsafe_b64decode(data + "=" * padding)


class SimpleJWTAuthenticator(Authenticator):
    """Simple HMAC-SHA256 JWT authenticator (no external deps)."""

    def __init__(self, secret: str, ttl_seconds: int = 3600) -> None:
        self._secret = secret.encode()
        self._ttl = ttl_seconds
        self._user_store: Dict[str, str] = {}

    def add_user(self, username: str, password_hash: str) -> None:
        self._user_store[username] = password_hash

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _sign(self, header_b64: str, payload_b64: str) -> str:
        message = f"{header_b64}.{payload_b64}".encode()
        signature = hmac.new(self._secret, message, hashlib.sha256).digest()
        return _b64_encode(signature)

    def _create_token(self, subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
        if extra_claims is None:
            extra_claims = {}
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": subject,
            "iat": int(time.time()),
            "exp": int(time.time()) + self._ttl,
            **extra_claims,
        }
        h = _b64_encode(json.dumps(header).encode())
        p = _b64_encode(json.dumps(payload).encode())
        s = self._sign(h, p)
        return f"{h}.{p}.{s}"

    def authenticate(self, credentials: Credentials) -> Optional[AuthToken]:
        stored_hash = self._user_store.get(credentials.username)
        if not stored_hash:
            logger.warning("Auth failed: unknown user %s", credentials.username)
            return None
        if stored_hash != self._hash_password(credentials.password):
            logger.warning("Auth failed: bad password for %s", credentials.username)
            return None
        token_str = self._create_token(credentials.username)
        logger.info("Auth success: %s", credentials.username)
        return AuthToken(token=token_str, subject=credentials.username, claims={})

    def verify_token(self, token: str) -> Optional[AuthToken]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            h, p, s = parts
            expected_sig = self._sign(h, p)
            if not hmac.compare_digest(s, expected_sig):
                logger.warning("Token signature invalid")
                return None
            payload = json.loads(_b64_decode(p))
            if payload.get("exp", 0) < time.time():
                logger.warning("Token expired")
                return None
            return AuthToken(token=token, subject=payload["sub"], claims=payload)
        except Exception as e:
            logger.error("Token verification error: %s", e)
            return None
