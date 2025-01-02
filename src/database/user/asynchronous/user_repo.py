from src.database.database import AsyncDatabase
from src.database.database_factory import DatabaseFactory

class UserRepository:
    def __init__(self, db: AsyncDatabase):
        self.db = db

    async def check_user_registration(self, user_number: str) -> bool:
        db = self.db
        result = await db.fetch_one(
            "SELECT * FROM users WHERE number = ?", 
            (user_number,)
        )
        return bool(result)
    
