from ..database.connect_db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Index, func
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import Users
    from .sensors import Sensors
    from .rooms import Rooms

class SensorViolations(Base):
    __tablename__ = "sensor_violations"
    
    __table_args__ = (
        Index('ix_violations_user_time', 'user_id', 'created_at'),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id", ondelete="CASCADE"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    
    exceeded_value: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    
    user: Mapped["Users"] = relationship("Users", back_populates="violations")
    sensor: Mapped["Sensors"] = relationship("Sensors")
    room: Mapped["Rooms"] = relationship("Rooms")