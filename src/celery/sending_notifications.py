from .init_celery import celery
from src.redis.redis_notifications import RedisNotifications
from src.business_logic.generating_values import GeneratingValuesSensors
from src.database.db_depends import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from src.models.rooms import Rooms
from src.models.users import Users
from src.models.sensors import Sensors
from src.models.sensor_violations import SensorViolations
from src.database.connect_db import async_session_maker
import asyncio

async def _send_notifi():
    async with RedisNotifications() as connection, async_session_maker() as db:
        tmp_rooms = await db.scalars(select(Rooms).
                                options(joinedload(Rooms.sensors),
                                joinedload(Rooms.users))
                               )
        rooms: list[Rooms] = tmp_rooms.all()
        admins: list[Users] = (await db.scalars(select(Users).where(Users.role == 'admin'))).all()
        tmp_sens: list[Sensors] = (await db.scalars(select(Sensors))).all()
        sens = {sen.name: sen.id for sen in tmp_sens}
        for room in rooms:
            all_users = room.users + admins
            obj = GeneratingValuesSensors(room.sensors)
            result: dict = obj.generation()
            for key, value in result.get('violations').items():
                for user in all_users:
                    violation = SensorViolations(
                        user_id = user.id,
                        sensor_id = sens[key],
                        exceeded_value = value
                    )
                    db.add(violation)
            await db.commit()
            await connection.publish(f"room:{room.number}", result)

@celery.task(queue="notifications")
def send_notifi():
    asyncio.run(_send_notifi())
