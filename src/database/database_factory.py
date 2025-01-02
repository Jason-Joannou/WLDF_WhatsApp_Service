from src.database.database import AsyncSQLiteDatabase, AsyncPostgresDatabase, PostgresDatabase, SQLiteDatabase, Database, AsyncDatabase
from typing import Union
class DatabaseFactory:
    # Factory for creating database instances
    @staticmethod
    def create_database(db_type: str, connection_params: str, is_async: bool = False) -> Union[Database, AsyncDatabase]:
        if db_type.lower() == "sqlite":
            return AsyncSQLiteDatabase(connection_params) if is_async else SQLiteDatabase(connection_params)
        elif db_type.lower() == "postgres":
            return AsyncPostgresDatabase(connection_params) if is_async else PostgresDatabase(connection_params)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")