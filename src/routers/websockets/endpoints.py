from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

router = APIRouter(
    prefix='/websockets',
    tags=['websockets']
)

@router.websocket("/sensors")
async def websocket_sensors(websocket: WebSocket):
    pass


