from ..database.connect_db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rooms import Rooms

class Sensors(Base):
    __tablename__ = "sensors"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    unit: Mapped[str]
    min_normal: Mapped[float]
    max_normal: Mapped[float]
    
    rooms: Mapped["Rooms"] = relationship("Rooms", secondary="room_sensor", back_populates="sensors")