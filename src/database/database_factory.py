from src.database.database import AsyncSQLiteDatabase, AsyncPostgresDatabase, PostgresDatabase, SQLiteDatabase
from typing import Union
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: str, connection_params: str) -> Union[Session, AsyncSession]:
        # Create appropriate database instance
        if db_type.lower() == "sqlite":
            db = AsyncSQLiteDatabase(connection_params)
            engine = db.get_engine()
            async_session = async_sessionmaker(engine, expire_on_commit=False)
            return async_session()
        elif db_type.lower() == "postgres":
            db = AsyncPostgresDatabase(connection_params)
            engine = db.get_engine()
            async_session = async_sessionmaker(engine, expire_on_commit=False)
            return async_session()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")