import json
from fastapi import WebSocket, status
from starlette.websockets import WebSocketDisconnect
from src.redis.redis_notifications import RedisNotifications

async def handle_redis_pubsub(websocket: WebSocket, channel: str, user_id: int, is_pattern: bool = False):
    async with RedisNotifications() as connection:
        async with connection.redis.pubsub() as pubsub:
            if is_pattern:
                await pubsub.psubscribe(channel)
            else:
                await pubsub.subscribe(channel)
            
            try:
                async for message in pubsub.listen():
                    if message["type"] in ["message", "pmessage"]:
                        data = message["data"].decode()
                        await websocket.send_json(json.loads(data))
            except WebSocketDisconnect:
                print(f"Клиент {user_id} отключился")
            except Exception as e:
                print(f"Ошибка в WebSocket для юзера {user_id}: {e}")
                if websocket.client_state.value == 1:
                    await websocket.close(code=status.WS_1011_INTERNAL_ERROR)