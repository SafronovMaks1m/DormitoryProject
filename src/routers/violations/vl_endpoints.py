from fastapi import APIRouter, status, Query, Body, Depends, HTTPException
from src.database.db_depends import get_async_db
from sqlalchemy import select, desc, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.sensor_violations import SensorViolations
from sqlalchemy.orm import joinedload
from src.models.users import Users
from src.models.rooms import Rooms
from src.models.sensors import Sensors
from src.auth.auth import get_current_user
from src.schemas.ViolationsSchema import ViolationList
from datetime import datetime, timezone

router = APIRouter(
    prefix='/violations',
    tags=['violations']
)

@router.get('/', response_model=ViolationList, status_code=status.HTTP_200_OK)
async def get_violations(
    unread: bool = Query(default=False),
    page: int | None = Query(default=None, ge=1),
    page_size: int | None= Query(default=None, ge=1, le=100),
    num_room: int | None = Query(default=None, ge=1),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    filters = []
    if num_room is not None:
        if user.role == "student":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A student cannot use the room filter")
        room_id = await db.scalar(select(Rooms.id).where(Rooms.number == num_room))
        if room_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no such room")
        filters.append(SensorViolations.room_id == room_id)
    
    if user.role == "student":
        filters.append(SensorViolations.user_id == user.id)
        
    if unread:
        if any([page, page_size, start_time, end_time]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail='Unread messages can only be received all at once'
            )
            
        messages = (await db.scalars(select(SensorViolations)
                                     .options(joinedload(SensorViolations.sensor),
                                              joinedload(SensorViolations.room))
                                     .where(*filters,
                                           SensorViolations.read_at == None)
                                     .order_by(desc(SensorViolations.created_at)))).all()
        
        return {"violations": messages, "total": len(messages)}
    
    if start_time is not None and end_time is not None and start_time > end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The time filter is set incorrectly")
    
    if start_time is not None:
        filters.append(SensorViolations.created_at >= start_time)
        
    if end_time is not None:
        filters.append(SensorViolations.created_at <= end_time)
    
    tmp = (select(SensorViolations)
           .options(joinedload(SensorViolations.sensor),
                    joinedload(SensorViolations.room))
           .where(*filters)
           .order_by(desc(SensorViolations.created_at)))
    
    if page is not None:
        if page_size is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The number of messages is not specified"
            )
        tmp = tmp.offset((page - 1) * page_size).limit(page_size)
        
    elif page_size is not None:
        tmp = tmp.limit(page_size)
    
    messages = (await db.scalars(tmp)).all()
    
    total = await db.scalar(select(func.count())
                                .select_from(SensorViolations)
                                .where(*filters))
    
    return {"violations": messages, "total": total}

@router.patch("/", status_code=status.HTTP_204_NO_CONTENT)
async def read_messages(
    time: datetime = Body(..., embed=True), 
    user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    await db.execute(
        update(SensorViolations)
        .where(SensorViolations.user_id == user.id)
        .where(SensorViolations.created_at <= time)
        .where(SensorViolations.read_at == None)
        .values(read_at=datetime.now(timezone.utc))
    )
    
    await db.commit()