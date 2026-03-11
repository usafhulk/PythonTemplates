"""Auth Example."""
import hashlib
from engineering_framework.backend.auth.core import SimpleJWTAuthenticator
from engineering_framework.backend.auth.interfaces import Credentials

auth = SimpleJWTAuthenticator(secret="my-secret-key")
auth.add_user("alice", hashlib.sha256(b"password123").hexdigest())

token = auth.authenticate(Credentials("alice", "password123"))
print(f"Token issued: {token.token[:40]}...")

verified = auth.verify_token(token.token)
print(f"Verified subject: {verified.subject}")
