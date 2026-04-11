from redis.asyncio import Redis
from .RedisNotificationsException import RedisNotificationsException
import json

class RedisNotifications:
    def __init__(self, host='127.0.0.1', port=6379, db=0): 
        self.host = host
        self.port = port
        self.db = db
        self._redis = None
    
    @property
    def redis(self) -> Redis:
        if self._redis is None:
            raise RedisNotificationsException("Please use the context manager")
        return self._redis
    
    async def publish(self, num_room: int, message: dict):
        message_json = json.dumps(message)
        await self.redis.publish(num_room, message_json)
    
    def subscribe(self):
        return self.redis.pubsub()
        
    async def __aenter__(self):
        self._redis = Redis(self.host, self.port, self.db)
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.redis:
            await self.redis.close()
        