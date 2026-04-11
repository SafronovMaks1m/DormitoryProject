from src.database.connect_db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sessions import Sessions
    from password_setup_token import PasswordSetupToken
    from .rooms import Rooms
    from .sensor_violations import SensorViolations
class Users(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"))
    
    name: Mapped[str]
    email: Mapped[str] = mapped_column(index=True, unique=True)
    hashed_password: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default = True)
    role: Mapped[str] = mapped_column(default="student", index=True)
    
    sessions: Mapped[list["Sessions"]] = relationship("Sessions", back_populates="user")
    password_setup_token: Mapped["PasswordSetupToken"] = relationship("PasswordSetupToken", back_populates="user")
    room: Mapped["Rooms"] = relationship("Rooms", back_populates="users")
    violations: Mapped["SensorViolations"] = relationship("SensorViolations", back_populates="user")