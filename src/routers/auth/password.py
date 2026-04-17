from fastapi import APIRouter, status, Depends, HTTPException, Query, Body, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
import hashlib
from src.models.users import Users as UsersModel
from src.models.password_setup_token import PasswordSetupToken
from src.schemas.UserSchema import UserPasswordSetup
from src.database.db_depends import get_async_db
from src.auth.password_hashing import hash_password
from src.business_logic.sending_token import SendToken
from src.celery.bg_tasks import send_messages
from pydantic import EmailStr

router = APIRouter()

@router.get("/setup-password", status_code=status.HTTP_200_OK)
async def get_setup_password_user(#bg: BackgroundTasks,
                                token: str = Query(...), db: AsyncSession = Depends(get_async_db)):
    incoming_hash = hashlib.sha256(token.encode()).hexdigest()
    res = await db.scalar(select(PasswordSetupToken).where(incoming_hash == PasswordSetupToken.hash_token))
    if res is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="The link is incorrect.")
    if datetime.now(timezone.utc) > res.expires_at:
        await db.execute(delete(PasswordSetupToken).where(PasswordSetupToken.id == res.id))
        tmp = SendToken.creating_token_instance(res.user)
        db_passwod_token = tmp.get("instance")
        db.add(db_passwod_token)
        await db.commit()
        #bg.add_task(SendToken.send_token_email, res.user.email, tmp.get("token"))
        send_messages.delay(res.user.email, tmp.get("token"))
        raise HTTPException(status_code=status.HTTP_410_GONE, 
                            detail="The link's lifespan has expired, and a new link has been sent to your email")
    return {"detail": "Okay"}
    
@router.post("/setup-password", status_code=status.HTTP_200_OK)
async def post_setup_password_user(user_password: UserPasswordSetup, #bg: BackgroundTasks,
                                   token: str = Query(...), db: AsyncSession = Depends(get_async_db)):
    incoming_hash = hashlib.sha256(token.encode()).hexdigest()
    res = await db.scalar(
        select(PasswordSetupToken)
        .options(
            joinedload(PasswordSetupToken.user) 
            .joinedload(UsersModel.sessions)
        )
        .where(PasswordSetupToken.hash_token == incoming_hash)
    )
    if res is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="The link is incorrect.")
    if datetime.now(timezone.utc) > res.expires_at:
        await db.execute(delete(PasswordSetupToken).where(PasswordSetupToken.id == res.id))
        tmp = SendToken.creating_token_instance(res.user)
        db_passwod_token = tmp.get("instance")
        db.add(db_passwod_token)
        await db.commit()
        #bg.add_task(SendToken.send_token_email, res.user.email, tmp.get("token"))
        send_messages.delay(res.user.email, tmp.get("token"))
        raise HTTPException(status_code=status.HTTP_410_GONE, 
                            detail="The link's lifespan has expired, and a new link has been sent to your email")
    db_user = res.user
    await db.execute(update(UsersModel).
                     where(UsersModel.id == db_user.id).
                     values(hashed_password = hash_password(user_password.password.get_secret_value())))
    for session in db_user.sessions:
        session.is_active = False
    await db.execute(delete(PasswordSetupToken).where(PasswordSetupToken.id == res.id))
    await db.commit()
    return {"detail": "The password has been created"}

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(#bg: BackgroundTasks, 
                          email: EmailStr = Body(...), db: AsyncSession = Depends(get_async_db)):
    db_user = await db.scalar(select(UsersModel).where(UsersModel.email == email))
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="There is no user with this email address")
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="User id blocked")
    tmp = SendToken.creating_token_instance(db_user)
    db_passwod_token = tmp.get("instance")
    db.add(db_passwod_token)
    await db.commit()
    await db.refresh(db_user)
    #bg.add_task(SendToken.send_token_email, db_user.email, tmp.get("token"))
    send_messages.delay(db_user.email, tmp.get("token"))
    return {"detail": "A link to change your password has been sent to your email"}