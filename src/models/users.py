from src.database.connect_db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sessions import Sessions
    from password_setup_token import PasswordSetupToken

class Users(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str]
    email: Mapped[str] = mapped_column(index=True, unique=True)
    hashed_password: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default = True)
    role: Mapped[str] = mapped_column(default="student")
    room_number: Mapped[int]
    
    sessions: Mapped[list["Sessions"]] = relationship("Sessions", back_populates="user")
    password_setup_token: Mapped["PasswordSetupToken"] = relationship("PasswordSetupToken", back_populates="user")