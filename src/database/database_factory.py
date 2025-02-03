# database_factory.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Union
import logging

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: str, connection_params: str) -> async_sessionmaker[AsyncSession]:
        """
        Create and return an async session maker for the specified database type
        """
        try:
            if db_type.lower() == "sqlite":
                url = f"sqlite+aiosqlite:///{connection_params}"
            elif db_type.lower() == "postgres":
                url = f"postgresql+asyncpg://{connection_params}"
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            engine = create_async_engine(
                url,
                echo=True,  # Set to False in production
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
            
            return async_sessionmaker(
                engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            
        except Exception as e:
            logging.error(f"Failed to create database connection: {e}")
            raise