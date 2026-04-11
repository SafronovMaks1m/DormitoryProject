from ..database.connect_db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import Users
    from .sensors import Sensors

class SensorViolations(Base):
    __tablename__ = "sensor_violations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id", ondelete="CASCADE"))
    
    exceeded_value: Mapped[float]
    is_read: Mapped[bool] = mapped_column(default=False)
    
    user: Mapped["Users"] = relationship("Users", back_populates="violations")
    sensor: Mapped["Sensors"] = relationship("Sensors")