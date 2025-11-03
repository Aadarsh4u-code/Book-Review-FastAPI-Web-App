from redis.asyncio import Redis

from app.core.config import setting

token_blocklist = Redis(host=setting.REDIS_HOST, port=setting.REDIS_PORT, db=0, decode_responses=True)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=setting.JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(name=jti)
    return jti is not None

