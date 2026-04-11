from ..database.connect_db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import Users
    from .sensors import Sensors

class Rooms(Base):
    __tablename__ = "rooms"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int]
    
    users: Mapped[list["Users"]] = relationship("Users", back_populates="room")
    sensors: Mapped[list["Sensors"]] = relationship("Sensors", secondary="room_sensor", back_populates="rooms")