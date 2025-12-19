import redis

from app.core.config import settings

def create_redis():
  return redis.ConnectionPool(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=0, 
    decode_responses=True
  )

pool = create_redis()

def get_redis() -> redis.Redis:
  return redis.Redis(connection_pool=pool)