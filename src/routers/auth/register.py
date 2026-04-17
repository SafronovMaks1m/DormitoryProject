from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.celery.bg_tasks import send_messages
from src.models.users import Users as UsersModel
from src.models.rooms import Rooms
from src.schemas.UserSchema import User as UserSchema, UserCreate
from src.database.db_depends import get_async_db
from src.auth.auth import get_current_admin
from src.business_logic.sending_token import SendToken

router = APIRouter()

@router.get("/", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_me_reg(cur_admin: UsersModel = Depends(get_current_admin)):
    return cur_admin

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, #bg: BackgroundTasks,
                      db: AsyncSession = Depends(get_async_db),
                      cur_admin: UsersModel = Depends(get_current_admin)):
    result = await db.scalar(select(UsersModel).where(UsersModel.email == user.email))
    if result:
        raise HTTPException(status_code=400, detail="User already exists")
    db_room = await db.scalar(select(Rooms).where(Rooms.number == user.room_number))
    if db_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no such room")
    db_user = UsersModel(
        name=user.name,
        room_id = db_room.id,
        email=user.email
    )
    db.add(db_user)

    tmp = SendToken.creating_token_instance(db_user)
    db.add(tmp.get("instance"))

    await db.commit()
    await db.refresh(db_user)

    send_messages.delay(db_user.email, tmp.get("token"))
    #bg.add_task(SendToken.send_token_email, db_user.email, tmp.get("token"))

    return {"detail": "User created, email sent"}