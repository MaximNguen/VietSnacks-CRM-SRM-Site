from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from typing import List
import logging
import uuid

from app.models.delivery import Delivery, DeliveryStatus
from delivery_service.app.services import delivery

class DeliveryRepository:
    """Класс-репозиторий для управления данными о доставках, обеспечивающий взаимодействие с базой данных."""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
    async def get_by_delivery_id(self, delivery_id: uuid.UUID) -> Delivery | None:
        self.logger.info(f"Получение доставки по ID: {delivery_id}")
        try:
            result = await self.db.scalar(select(Delivery).where(Delivery.delivery_id == delivery_id))
        except Exception as e:
            self.logger.error(f"Ошибка при получении доставки по ID: {delivery_id}, ошибка: {e}")
            result = None
        return result
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Delivery]:
        self.logger.info("Получение всех доставок")
        try:
            result = await self.db.scalars(select(Delivery).offset(skip).limit(limit))
        except Exception as e:
            self.logger.error(f"Ошибка при получении всех доставок, ошибка: {e}")
            result = []
        return list(result)
    
    async def create_delivery(
        self,
        *,
        order_id: uuid.UUID,
        delivery_person_id: uuid.UUID | None = None,
        address: str,
        scheduled_time: datetime | None = None,
        delivery_fee: float = 0.0,
        status: DeliveryStatus | None = None,
    ) -> Delivery:
        self.logger.info(
            "Создание новой доставки (order_id=%s, delivery_person_id=%s)",
            order_id,
            delivery_person_id,
        )

        delivery = Delivery(
            order_id=order_id,
            address=address,
            delivery_person_id=delivery_person_id,
            scheduled_time=scheduled_time,
            delivery_fee=delivery_fee,
        )

        if status is not None:
            delivery.status = status

        try:
            self.db.add(delivery)
            await self.db.commit()
            await self.db.refresh(delivery)
        except Exception as e:
            self.logger.error(f"Ошибка при создании доставки: {delivery}, ошибка: {e}")
            await self.db.rollback()
            raise
        return delivery
    
    async def update_delivery(
        self,
        delivery_id: uuid.UUID,
        status: str | None,
    ) -> Delivery:
        self.logger.info(f"Обновление доставки (delivery_id={delivery.delivery_id})")
        try:
            await self.db.execute(
                update(Delivery).where(Delivery.delivery_id == delivery_id).values(status=status)
            )
            await self.db.commit()
            await self.db.refresh(delivery)
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении доставки: {delivery}, ошибка: {e}")
            await self.db.rollback()
            raise
        return delivery
    
    async def delete_delivery(self, delivery_id: uuid.UUID) -> None:
        self.logger.info(f"Удаление доставки (delivery_id={delivery_id})")
        try:
            delivery = await self.get_by_delivery_id(delivery_id)
            if delivery:
                await self.db.delete(delivery)
                await self.db.commit()
        except Exception as e:
            self.logger.error(f"Ошибка при удалении доставки с ID: {delivery_id}, ошибка: {e}")
            await self.db.rollback()
            raise