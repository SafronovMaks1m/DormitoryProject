from pydantic import BaseModel, Field, EmailStr, ConfigDict, SecretStr

class UserCreate(BaseModel):
    """
    Модель для создания пользователя
    """
    name: str = Field(pattern="^[A-Za-zА-Яа-яЁё]+([ -][A-Za-zА-Яа-яЁё]+)*$", description="имя пользователя")
    room_number: int = Field(description="Номер комнаты")
    email: EmailStr = Field(description="Email пользователя")


class User(BaseModel):
    """
    Модель для ответа с данными пользователя
    """
    id: int = Field(description="id пользователя")
    name: str = Field(description="имя пользователя")
    room_number: int = Field(description="Номер комнаты")
    email: EmailStr = Field(description="Email пользователя")
    role: str = Field(description="Роль пользоваьтеля")
    
    model_config = ConfigDict(from_attributes=True)
    
class UserPasswordSetup(BaseModel):
    password: SecretStr = Field(min_length=8, description="длина минимум 8 символов")

class UserLogin(BaseModel):
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(description="Пароль пользователя")