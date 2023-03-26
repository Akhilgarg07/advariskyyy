import redis
import os
import logging

Logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)

Logger.info(f"Redis host: {REDIS_HOST}, port: {REDIS_PORT}, db: {REDIS_DB}")


class RedisCache:
    def __init__(self):
        self.redis_pool = redis.ConnectionPool(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        self.redis_client = redis.Redis(connection_pool=self.redis_pool)

    def get(self, name):
        return self.redis_client.get(name)

    def set_(self, name, value, expiration_time: int = 3600):
        self.redis_client.set(name, value, expiration_time)

    def delete_key(self, key: str) -> bool:
        try:
            self.redis_client.delete(key)
            return True
        except redis.exceptions.RedisError:
            return False


def get_cache():
    return RedisCache()
