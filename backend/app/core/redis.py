import redis.asyncio as redis
from typing import Optional
import json

class RedisClient:
    def __init__(self) -> None:
        self.client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        from app.core.config import REDIS_URL
        self.client = await redis.from_url(REDIS_URL, decode_responses=True)

    async def disconnect(self) -> None:
        if self.client:
            await self.client.close()

    async def set(self, key: str, value: str, expire: int = 3600) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        await self.client.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.get(key)

    async def delete(self, key: str) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.exists(key)

    async def setex(self, key: str, seconds: int, value: str) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        await self.client.setex(key, seconds, value)

    async def get_json(self, key: str) -> Optional[dict]:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def set_json(self, key: str, value: dict, expire: int = 3600) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        await self.client.set(key, json.dumps(value), ex=expire)

redis_client = RedisClient()
