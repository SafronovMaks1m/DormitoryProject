from redis.asyncio import Redis
from .RedisNotificationsException import RedisNotificationsException
import json

class AsyncRedisNotifications:
    def __init__(self, host='redis', port=6379, db=0): 
        self.host = host
        self.port = port
        self.db = db
        self._redis = None
    
    @property
    def redis(self) -> Redis:
        if self._redis is None:
            raise RedisNotificationsException("Please use the context manager")
        return self._redis
    
    async def publish(self, room_id: int, message: dict):
        message_json = json.dumps(message)
        await self.redis.publish(f"room:{room_id}", message_json)
        
    async def __aenter__(self):
        self._redis = Redis(host=self.host, port=self.port, db=self.db)
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.redis:
            await self.redis.close()
        