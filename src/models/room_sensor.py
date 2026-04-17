from ..database.connect_db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint

class RoomSensor(Base):
    __tablename__ = "room_sensor"
    
    __table_args__ = (
        UniqueConstraint("room_id", "sensor_id", name="uq_room_sensor_id"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id", ondelete="CASCADE"))
    
    