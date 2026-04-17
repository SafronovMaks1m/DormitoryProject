from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from .UserSchema import Room

class Sensor(BaseModel):
    name: str = Field(description="Название датчика")
    unit: str = Field(description="Единица измерения")
    min_normal: float = Field(description="Минимальное нормальное значение")
    max_normal: float = Field(description="Максимальное нормальное значение")
    
    model_config = ConfigDict(from_attributes=True)
    
class Violation(BaseModel):
    exceeded_value: float = Field(description="Значение нарушения")
    created_at: datetime = Field(description="Время нарушения")
    sensor: Sensor = Field(description="Датчик, на котором зафиксирвано нарушение")
    room: Room = Field(description="Комната, в которой произошли нарушения")
    
    model_config = ConfigDict(from_attributes=True) 

class ViolationList(BaseModel):
    violations: list[Violation] = Field(description="Список нарушений")
    total: int = Field(description="Число найденных нарушений")
    
    model_config = ConfigDict(from_attributes=True)