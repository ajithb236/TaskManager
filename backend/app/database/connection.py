import asyncpg
from typing import Optional, List, Dict, Any
from app.core.config import DATABASE_URL, DATABASE_POOL_MIN_SIZE, DATABASE_POOL_MAX_SIZE, DATABASE_COMMAND_TIMEOUT

class Database:
    def __init__(self) -> None:
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        # Remove +asyncpg driver from URL for asyncpg.create_pool
        url = DATABASE_URL.replace("+asyncpg", "")
        self.pool = await asyncpg.create_pool(
            url,
            min_size=DATABASE_POOL_MIN_SIZE,
            max_size=DATABASE_POOL_MAX_SIZE,
            command_timeout=DATABASE_COMMAND_TIMEOUT
        )

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args: Any) -> str:
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args: Any) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> Optional[Dict[str, Any]]:
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)

database = Database()
