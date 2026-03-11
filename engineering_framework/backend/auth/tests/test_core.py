"""Auth Tests."""
import pytest
from ..core import SimpleJWTAuthenticator
from ..interfaces import Credentials


def test_authenticate_valid_user():
    import hashlib
    auth = SimpleJWTAuthenticator(secret="test-secret")
    auth.add_user("alice", hashlib.sha256(b"password123").hexdigest())
    token = auth.authenticate(Credentials("alice", "password123"))
    assert token is not None
    assert token.subject == "alice"


def test_authenticate_wrong_password():
    import hashlib
    auth = SimpleJWTAuthenticator(secret="test-secret")
    auth.add_user("alice", hashlib.sha256(b"password123").hexdigest())
    token = auth.authenticate(Credentials("alice", "wrongpassword"))
    assert token is None


def test_verify_valid_token():
    import hashlib
    auth = SimpleJWTAuthenticator(secret="test-secret")
    auth.add_user("bob", hashlib.sha256(b"secret").hexdigest())
    token = auth.authenticate(Credentials("bob", "secret"))
    verified = auth.verify_token(token.token)
    assert verified is not None
    assert verified.subject == "bob"


def test_verify_invalid_token():
    auth = SimpleJWTAuthenticator(secret="test-secret")
    result = auth.verify_token("invalid.token.here")
    assert result is None
