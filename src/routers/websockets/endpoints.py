from fastapi import APIRouter, WebSocket, Depends, status
from starlette.websockets import WebSocketDisconnect
from src.models.users import Users
from src.auth.auth import get_user_for_socket, get_current_admin_for_socket
from src.redis.redis_notifications import RedisNotifications
from sqlalchemy import select
from src.models.rooms import Rooms
from src.database.connect_db import async_session_maker
from .logic_sending import handle_redis_pubsub

router = APIRouter(
    prefix='/websockets',
    tags=['websockets']
)

@router.websocket("/sensors")
async def websocket_sensors_user(websocket: WebSocket, user: Users | None = Depends(get_user_for_socket)):
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Insufficient access rights")
        return
    
    await websocket.accept()
    await handle_redis_pubsub(websocket, f"room:{user.room_id}", user.id)

@router.websocket("/panel-admin")
async def websocket_admin_all(websocket: WebSocket, user: Users | None = Depends(get_current_admin_for_socket)):
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Insufficient access rights")
        return
    
    await websocket.accept()
    await handle_redis_pubsub(websocket, "room:*", user.id, is_pattern=True)

@router.websocket("/panel-admin/{num_room}")
async def websocket_admin_single_room(websocket: WebSocket, num_room: int, 
                                      user: Users | None = Depends(get_current_admin_for_socket)):
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Insufficient access rights")
        return
    
    async with async_session_maker() as db:
        room_id = await db.scalar(select(Rooms.id).where(Rooms.number == num_room))
       
    if room_id is None:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA, reason="Room not found")
        return
    
    await websocket.accept()
    await handle_redis_pubsub(websocket, f"room:{room_id}", user.id)


