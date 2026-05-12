from pydantic import BaseModel, Field
from pydantic import ConfigDict
import uuid
from datetime import datetime

class DeliveryCreate(BaseModel):
    """Класс-схема для создания новой доставки, определяющий необходимые поля и их типы."""
    model_config = ConfigDict(from_attributes=True)
    
    order_id: uuid.UUID = Field(..., description="ID заказа, для которого создается доставка")
    delivery_person_id: uuid.UUID | None = Field(None, description="ID курьера, если назначен")
    address: str = Field(..., description="Адрес доставки")
    scheduled_time: datetime | None = Field(None, description="Запланированное время доставки в формате ISO 8601")
    delivery_fee: float = Field(0.0, description="Стоимость доставки")
    
class DeliveryUpdate(BaseModel):
    """Класс-схема для обновления информации о доставке, определяющий поля, которые могут быть изменены."""
    model_config = ConfigDict(from_attributes=True)
    
    status: str | None = Field(None, description="Новый статус доставки")