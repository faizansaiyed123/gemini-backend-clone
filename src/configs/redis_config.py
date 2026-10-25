import redis
from dotenv import load_dotenv
import os
from src.configs.settings import settings
from upstash_redis import Redis as SyncRedis
from upstash_redis.asyncio import Redis as AsyncRedis
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))



redis_client = AsyncRedis(
    url=settings.UPSTASH_REDIS_REST_URL,
    token=settings.UPSTASH_REDIS_REST_TOKEN
)

redis_sync_client = SyncRedis(
    url=settings.UPSTASH_REDIS_REST_URL,
    token=settings.UPSTASH_REDIS_REST_TOKEN
)
