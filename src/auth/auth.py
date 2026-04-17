from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect, status
import jwt, secrets, hashlib
from src.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM
from fastapi.security import APIKeyCookie
from datetime import datetime, timezone, timedelta
from src.models.users import Users
from src.models.sessions import Sessions
from src.database.db_depends import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.sessions import Sessions
from sqlalchemy import select
from src.routers.websockets.exceptions import WebSocketTokenExpiredException
from sqlalchemy.orm import joinedload
from src.database.connect_db import async_session_maker

access_token = APIKeyCookie(name="access_token", auto_error=False)
refresh_cookie = APIKeyCookie(name="refresh_token", auto_error=False)

def create_access_token(data: dict):
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)

def create_refresh_token() -> dict:
    refresh_token = secrets.token_urlsafe(64)
    hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    return {"token": refresh_token, "hashed_token": hashed}

async def get_current_session(token: str = Depends(access_token),
                           db: AsyncSession = Depends(get_async_db)):
    """
    Проверяет JWT и возвращает сессию пользователя из базы.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        session_id: int = int(payload.get("sub"))
        if session_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError as e:
        raise credentials_exception
    session = await db.scalar(select(Sessions)
                              .options(joinedload(Sessions.user)
                                       .joinedload(Users.room))
                              .where(Sessions.id == session_id))
    if session is None or session.revoked or not session.is_active or not session.user.is_active:
        raise credentials_exception
    if not session.user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is blocked"
        )
    return session

async def get_current_session_optional(token: str = Depends(access_token), db: AsyncSession = Depends(get_async_db)):
    try:
        return await get_current_session(token, db)
    except HTTPException:
        return None

async def get_user_for_socket(websocket: WebSocket):
    async with async_session_maker() as db:
        try:
            token = websocket.cookies.get("access_token")
            if token is None:
                return None
            session = await get_current_session(token=token, db=db)
            return session.user
        except HTTPException as e:
            if e.detail == "Token has expired": 
                await websocket.accept()
                await websocket.close(code=4001, reason="Token expired")
                raise WebSocketDisconnect()
            return None

async def get_current_student_for_socket(current_user: Users | None = Depends(get_user_for_socket)):
    """
    Проверяет, что пользователь имеет роль 'student' в вебсокете.
    """
    if current_user is not None and current_user.role == "student":
        return current_user
    return None

async def get_current_admin_for_socket(current_user: Users | None = Depends(get_user_for_socket)):
    """
    Проверяет, что пользователь имеет роль 'admin' в вебсокете.
    """
    if current_user is not None and current_user.role == "admin":
        return current_user
    return None
    
async def get_current_user(current_session: Sessions = Depends(get_current_session)):
    """
    Проверяет JWT и возвращает пользователя из базы.
    """
    return current_session.user

async def get_current_student(current_user: Users = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'student'.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Student can perform this action")
    return current_user

async def get_current_admin(current_user: Users = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'admin'.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin can perform this action")
    return current_user