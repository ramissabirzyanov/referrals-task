from redis.asyncio import Redis


async def get_redis() -> Redis:
    return Redis(
        host="redis",
        port=6379,
        db=0,
        decode_responses=True
    )
