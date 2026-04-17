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
from src.database.connect_db import session_maker
from sqlalchemy.orm import selectinload
from src.business_logic.sending_token import SendToken
from celery import shared_task
import asyncio

def _send_notifi():
    with RedisNotifications() as connection, session_maker() as db:
        tmp_rooms = db.scalars(select(Rooms).
                                options(selectinload(Rooms.sensors),
                                selectinload(Rooms.users))
                               )
        rooms: list[Rooms] = tmp_rooms.all()
        admins: list[Users] = db.scalars(select(Users).where(Users.role == 'admin')).all()
        tmp_sens: list[Sensors] = db.scalars(select(Sensors)).all()
        sens = {sen.name: sen.id for sen in tmp_sens}
        for room in rooms:
            all_users = room.users + admins
            obj = GeneratingValuesSensors(room.sensors)
            result: dict = obj.generation()
            for key, value in result.get('violations').items():
                for user in all_users:
                    new_violation = SensorViolations(
                        user_id = user.id,
                        sensor_id = sens[key],
                        room_id = room.id,
                        exceeded_value = value
                    )
                    db.add(new_violation)
                    db.flush()
                    
            db.commit()
            connection.publish(room.id, result)

@shared_task(queue="notifications")
def send_notifi():
    _send_notifi()
    
@shared_task(queue="messages")
def send_messages(email: str, token: str):
    SendToken.send_token_email(email=email, token=token)