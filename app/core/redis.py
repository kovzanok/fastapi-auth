from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings

def create_redis():
  return ConnectionPool(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=0, 
    decode_responses=True
  )

pool = create_redis()

def get_redis() -> Redis:
  return Redis(connection_pool=pool)