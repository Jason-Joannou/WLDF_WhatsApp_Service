from src.database.database import Database
from src.database.database_factory import DatabaseFactory
class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def check_user_registration(self, user_number: str) -> bool:
        db = self.db
        result = db.fetch_one("SELECT * FROM users WHERE number = ?", (user_number,))
        return bool(result)