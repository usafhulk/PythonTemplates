"""Secrets Manager Example."""
from engineering_framework.infra.secrets_manager.core import InMemorySecretsManager

mgr = InMemorySecretsManager()
mgr.set_secret("database_password", "p@ssw0rd!")
mgr.set_secret("api_key", "sk-abc123")

db_pass = mgr.get_secret("database_password")
api_key = mgr.get_secret("api_key")
print(f"Secrets available: {mgr.list_secrets()}")
print(f"DB password retrieved: {'***' if db_pass else 'NOT FOUND'}")
