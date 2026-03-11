"""DI Container Example."""
from engineering_framework.core.dependency_injection.core import DIContainer

class DatabaseConnection:
    def query(self, sql: str) -> list:
        return []

class UserRepository:
    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

container = DIContainer()
container.register(DatabaseConnection, DatabaseConnection)
container.register(UserRepository, UserRepository)
repo = container.resolve(UserRepository)
print(repo.db.query("SELECT * FROM users"))
