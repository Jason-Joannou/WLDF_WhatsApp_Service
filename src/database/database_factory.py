from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import logging

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: str, connection_params: str) -> async_sessionmaker[AsyncSession]:
        """
        Create and return an async session maker for the specified database type
        """
        try:
            engine_kwargs = {
                "echo": True,  # Set to False in production
            }

            if db_type.lower() == "sqlite":
                url = f"sqlite+aiosqlite:///{connection_params}"
                # SQLite-specific settings (no pooling needed)
            
            elif db_type.lower() == "postgres":
                url = f"postgresql+asyncpg://{connection_params}"
                # Add pooling configuration only for PostgreSQL
                engine_kwargs.update({
                    "pool_pre_ping": True,
                    "pool_size": 5,
                    "max_overflow": 10
                })
            
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            engine = create_async_engine(url, **engine_kwargs)
            
            return async_sessionmaker(
                engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            
        except Exception as e:
            logging.error(f"Failed to create database connection: {e}")
            raise