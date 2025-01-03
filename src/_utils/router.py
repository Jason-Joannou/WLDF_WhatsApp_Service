from dotenv import load_dotenv
from src.database.database_factory import DatabaseFactory
from src.database.user.asynchronous.user_repo import UserRepository
import os

load_dotenv()

async def state_router(from_number: str) -> str:

    db = DatabaseFactory.create_database(os.getenv("DATABASE_TYPE"), os.getenv("DATABASE_URL"), is_async=True)

    user_repo = UserRepository(db)

    registered = await user_repo.check_user_registration(from_number)

    if registered:
        pass
    

    return "unregistered"
