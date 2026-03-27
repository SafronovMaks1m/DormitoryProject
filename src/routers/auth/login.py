from fastapi import APIRouter, Depends, HTTPException, Response, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta
import hashlib
from src.models.users import Users as UsersModel
from src.models.sessions import Sessions as SessionsModel
from src.schemas.UserSchema import UserLogin
from src.database.db_depends import get_async_db
from src.auth.password_hashing import verify_password
from src.auth.auth import get_current_session_optional, create_access_token, create_refresh_token, refresh_cookie
from src.config import REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter()

@router.get("/login", status_code=status.HTTP_200_OK)
async def get_login(session: SessionsModel = Depends(get_current_session_optional)):
    if session is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are already logged in"
        )
    return {"detail": "You can log in"}

@router.post("/login", status_code=status.HTTP_200_OK) #response_model=UserSchema
async def login(user: UserLogin, response: Response,
                device: str = Header(...), db: AsyncSession = Depends(get_async_db),
                session: SessionsModel = Depends(get_current_session_optional)):
    if session is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are already logged in"
        )
    db_user = await db.scalar(
        select(UsersModel)
        .options(selectinload(UsersModel.sessions))
        .where(UsersModel.email == user.email, UsersModel.is_active)
    )
    if db_user is None or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or incorrect password")
    cur_session = None    
    for session in db_user.sessions:
        if session.device_id == device:
            cur_session = session
            break
    tmp = create_refresh_token()
    if cur_session is None:
        cur_session = SessionsModel(
            device_id = device,
            refresh_token_hash = tmp.get("hashed_token"),
            expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            user = db_user
        )
        db.add(cur_session)
    else:
        if not cur_session.is_active or cur_session.revoked:
            cur_session.revoked = False
            cur_session.is_active = True
            cur_session.refresh_token_hash = tmp.get("hashed_token")
            cur_session.expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    await db.commit()
    await db.refresh(cur_session)
    access_token = create_access_token(data={"sub": str(cur_session.id)})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        max_age=30*60
    )
    response.set_cookie(
        key="refresh_token",
        value=tmp.get("token"),
        httponly=True,
        secure=True,
        max_age=30*24*60*60
    )
    # return db_user
    return access_token

@router.post("/refresh-token")
async def create_new_access_token(response: Response, 
                                  refresh_token: str = Depends(refresh_cookie), 
                                  db: AsyncSession = Depends(get_async_db)):
    try:
        hashed_refresh_token = hashlib.sha256(refresh_token.encode()).hexdigest()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh-token")
    cur_session = await db.scalar(
            select(SessionsModel).
            where(SessionsModel.refresh_token_hash == hashed_refresh_token, 
                  SessionsModel.is_active, SessionsModel.revoked == False)
        )
    if cur_session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh-token")
    if datetime.now(timezone.utc) > cur_session.expires_at:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The token's lifetime has expired")
    new_access_token = create_access_token({"sub": str(cur_session.id)})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30*60
    )

    return {"detail": "Access token refreshed"}
