import redis.asyncio as redis
import time

from src.core.config import settings


class RedisClient:
    def __init__(self):
        self.redis_client = None


    # Connect to Redis | Called internally
    async def init_redis(self):
        """Initialize Redis connection if not already initialized."""
        if not self.redis_client:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8",
            )


    # Disconnect from Redis | On shutdown
    async def close_redis(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None


    # Mark token as revoked | logout / refresh
    async def add_to_blocklist(self, jti: str, exp: int | None = None):
        """Revoke a token by storing its JTI with TTL"""
        if not self.redis_client:
            await self.init_redis()
        ttl = max(1, int(exp - time.time())) if exp else settings.JTI_EXPIRY
        await self.redis_client.setex(f"revoked:{jti}", ttl, "1")


    # Check if token is revoked | middleware
    async def is_token_revoked(self, jti: str) -> bool:
        """Check if a token jti is in the blocklist."""
        if not self.redis_client:
            await self.init_redis()
        return await self.redis_client.exists(f"revoked:{jti}") == 1


    # Save active refresh token | login / refresh
    async def store_refresh_token(self, user_id: str, jti: str, exp: int):
        """Save active refresh token (for tracking per user)"""
        if not self.redis_client:
            await self.init_redis()
        ttl = max(1, int(exp - time.time()))
        await self.redis_client.setex(f"user_refresh_tokens:{user_id}:{jti}", ttl, "active")


    # Delete all refresh tokens for user | logout / revoke
    async def revoke_user_refresh_tokens(self, user_id: str):
        """Revoke all refresh tokens of user"""
        if not self.redis_client:
            await self.init_redis()
        pattern = f"user_refresh_tokens:{user_id}:*"
        keys = await self.redis_client.keys(pattern)
        for key in keys:
            await self.redis_client.delete(key)


    # List revoked tokens for debugging | admin/debug
    async def show_all_revoked_tokens(self):
        """List all revoked tokens currently stored in Redis."""
        if not self.redis_client:
            await self.init_redis()

        keys = await self.redis_client.keys("revoked:*")
        results = []
        for key in keys:
            value = await self.redis_client.get(key)
            ttl = await self.redis_client.ttl(key)
            results.append({"key": key, "value": value, "ttl": ttl})
        return results


# Create global instance
redis_client = RedisClient()