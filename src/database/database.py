from abc import ABC, abstractmethod
import logging
from typing import Optional, Any, List, Tuple, Dict, Generic, TypeVar
from contextlib import contextmanager, asynccontextmanager
import sqlite3
import psycopg2
import aiosqlite
import asyncpg

T = TypeVar('T')
AsyncT = TypeVar('AsyncT')

# Base Interface for Synchronous Operations
class Database(ABC, Generic[T]):
    """Abstract base class for synchronous database operations"""
    
    @abstractmethod
    def get_connection(self) -> T:
        """Get a database connection"""
        pass
    
    @abstractmethod
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """Fetch a single row"""
        pass
    
    @abstractmethod
    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Fetch multiple rows"""
        pass
    
    @abstractmethod
    def execute(self, query: str, params: Tuple = ()) -> None:
        """Execute a query"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the database connection"""
        pass
    
    @abstractmethod
    @contextmanager
    def transaction(self):
        """Context manager for transactions"""
        pass

# Base Interface for Asynchronous Operations
class AsyncDatabase(ABC, Generic[AsyncT]):
    """Abstract base class for async database operations"""
    
    @abstractmethod
    async def get_connection(self) -> AsyncT:
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

# Synchronous Implementations
class SQLiteDatabase(Database[sqlite3.Connection]):
    """Synchronous SQLite implementation"""
    
    def __init__(self, database: str):
        self.database = database
        self._connection: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self.database)
                self._connection.row_factory = sqlite3.Row
            except Exception as e:
                logging.error(f"Failed to connect to SQLite database: {e}")
                raise
        return self._connection
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in rows]
    
    def execute(self, query: str, params: Tuple = ()) -> None:
        with self.transaction() as conn:
            conn.execute(query, params)
    
    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def transaction(self):
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

class PostgresDatabase(Database[psycopg2.extensions.connection]):
    """Synchronous PostgreSQL implementation"""
    
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._connection: Optional[psycopg2.extensions.connection] = None
    
    def get_connection(self) -> psycopg2.extensions.connection:
        if self._connection is None:
            try:
                self._connection = psycopg2.connect(self.dsn)
            except Exception as e:
                logging.error(f"Failed to connect to PostgreSQL database: {e}")
                raise
        return self._connection
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
        return None
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def execute(self, query: str, params: Tuple = ()) -> None:
        with self.transaction() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
    
    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def transaction(self):
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

# Asynchronous Implementations
class AsyncSQLiteDatabase(AsyncDatabase[aiosqlite.Connection]):
    """Asynchronous SQLite implementation"""
    
    def __init__(self, database: str):
        self.database = database
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def get_connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            try:
                self._connection = await aiosqlite.connect(self.database)
                self._connection.row_factory = aiosqlite.Row
            except Exception as e:
                logging.error(f"Failed to connect to SQLite database: {e}")
                raise
        return self._connection
    
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
    
    async def get_connection(self) -> asyncpg.Connection:
        if self._pool is None:
            try:
                # Create a connection pool instead of a single connection
                self._pool = await asyncpg.create_pool(self.dsn)
            except Exception as e:
                logging.error(f"Failed to create PostgreSQL connection pool: {e}")
                raise
        return await self._pool.acquire()
    
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