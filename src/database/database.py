from abc import ABC, abstractmethod
import logging
from typing import Optional, Any, List, Tuple, Dict, Generic, TypeVar
from contextlib import contextmanager, asynccontextmanager
import sqlite3
import aiosqlite
import asyncpg
import psycopg2
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

AsyncT = TypeVar('AsyncT')

# Base Interface for Asynchronous Operations
class AsyncDatabase(ABC, Generic[AsyncT]):
    """Abstract base class for async database operations"""
    
    @abstractmethod
    async def get_connection(self) -> AsyncT:
        pass

    @abstractmethod
    async def get_engine(self) -> AsyncEngine:
        """Get SQLAlchemy async engine"""
        pass
    
    @abstractmethod
    async def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        pass
    
    @abstractmethod
    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        pass
    
    @abstractmethod
    async def execute(self, query: str, params: Tuple = ()) -> None:
        pass
    
    @abstractmethod
    async def close(self) -> None:
        pass
    
    @abstractmethod
    @asynccontextmanager
    async def transaction(self):
        pass

# Asynchronous Implementations
class AsyncSQLiteDatabase(AsyncDatabase[aiosqlite.Connection]):
    """Asynchronous SQLite implementation"""
    
    def __init__(self, database: str):
        self.database = database
        self._connection: Optional[aiosqlite.Connection] = None
        self._engine: Optional[AsyncEngine] = None
    
    async def get_connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            try:
                self._connection = await aiosqlite.connect(self.database)
                self._connection.row_factory = aiosqlite.Row
            except Exception as e:
                logging.error(f"Failed to connect to SQLite database: {e}")
                raise
        return self._connection
    
    def get_engine(self) -> AsyncEngine:
        """Get SQLAlchemy async engine for SQLite"""
        if self._engine is None:
            self._engine = create_async_engine(
                f"sqlite+aiosqlite:///{self.database}",
                future=True
            )
        return self._engine
    
    async def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        conn = await self.get_connection()
        async with conn.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        conn = await self.get_connection()
        async with conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def execute(self, query: str, params: Tuple = ()) -> None:
        async with self.transaction() as conn:
            await conn.execute(query, params)
    
    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    @asynccontextmanager
    async def transaction(self):
        conn = await self.get_connection()
        try:
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise

class AsyncPostgresDatabase(AsyncDatabase[asyncpg.Connection]):
    """Asynchronous PostgreSQL implementation"""
    
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._connection: Optional[asyncpg.Connection] = None
        self._pool: Optional[asyncpg.Pool] = None
        self._engine: Optional[AsyncEngine] = None
    
    async def get_connection(self) -> asyncpg.Connection:
        if self._pool is None:
            try:
                # Create a connection pool instead of a single connection
                self._pool = await asyncpg.create_pool(self.dsn)
            except Exception as e:
                logging.error(f"Failed to create PostgreSQL connection pool: {e}")
                raise
        return await self._pool.acquire()
    
    def get_engine(self) -> AsyncEngine:
        """Get SQLAlchemy async engine for PostgreSQL"""
        if self._engine is None:
            self._engine = create_async_engine(
                f"postgresql+asyncpg://{self.dsn}",
                future=True
            )
        return self._engine
    
    async def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
    
    async def execute(self, query: str, params: Tuple = ()) -> None:
        async with self.transaction() as conn:
            await conn.execute(query, *params)
    
    async def execute_many(self, query: str, params: List[Tuple]) -> None:
        """Execute the same query with different parameters"""
        async with self.transaction() as conn:
            await conn.executemany(query, params)
    
    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    @asynccontextmanager
    async def transaction(self):
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                yield conn