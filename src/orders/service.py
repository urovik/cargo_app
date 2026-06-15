from src.db.db_manager import TransactionDbManager
from src.orders.schemas import OrderCreate, OrderUpdate
from src.orders.models import OrderStatus
from math import radians, sin, cos, sqrt, atan2

class OrderService:
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Расчет расстояния между двумя точками по формуле гаверсинуса"""
        R = 6371  # Радиус Земли в км
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def calculate_price(distance_km: float, weight: float) -> float:
        """Расчет стоимости доставки"""
        base_price = 100  # базовая стоимость
        price_per_km = 50  # стоимость за км
        weight_surcharge = weight * 10  # надбавка за вес
        
        return base_price + (distance_km * price_per_km) + weight_surcharge
    
    @staticmethod
    async def create_order(user_id: int, order_data: OrderCreate) -> dict:
        async with TransactionDbManager() as db:
            # Рассчитываем расстояние
            distance = OrderService.calculate_distance(
                order_data.pickup_lat, order_data.pickup_lng,
                order_data.delivery_lat, order_data.delivery_lng
            )
            
            # Рассчитываем цену
            price = OrderService.calculate_price(distance, order_data.cargo_weight)
            
            # Создаем заказ
            order = await db.order_repo.create(
                user_id=user_id,
                pickup_address=order_data.pickup_address,
                pickup_lat=order_data.pickup_lat,
                pickup_lng=order_data.pickup_lng,
                delivery_address=order_data.delivery_address,
                delivery_lat=order_data.delivery_lat,
                delivery_lng=order_data.delivery_lng,
                cargo_description=order_data.cargo_description,
                cargo_weight=order_data.cargo_weight,
                cargo_volume=order_data.cargo_volume,
                price=price,
                distance_km=distance
            )
            
            await db.commit()
            return {"order": order, "distance_km": distance, "price": price}
    
    @staticmethod
    async def get_user_orders(user_id: int) -> list:
        async with TransactionDbManager() as db:
            orders = await db.order_repo.get_by_user_id(user_id)
            return orders
    
    @staticmethod
    async def get_order_by_id(order_id: int, user_id: int = None) -> dict | None:
        async with TransactionDbManager() as db:
            order = await db.order_repo.get_by_id(order_id)
            
            if not order:
                return None
            
            # Если указан user_id, проверяем принадлежность заказа
            if user_id and order.user_id != user_id:
                return None
            
            return order
    
    @staticmethod
    async def update_order(order_id: int, user_id: int, order_data: OrderUpdate) -> dict | None:
        async with TransactionDbManager() as db:
            # Проверяем, что заказ существует и принадлежит пользователю
            order = await db.order_repo.get_by_id(order_id)
            
            if not order or order.user_id != user_id:
                return None
            
            # Нельзя редактировать заказ, который уже принят или в работе
            if order.status != OrderStatus.PENDING:
                raise ValueError(f"Cannot update order with status {order.status}")
            
            # Обновляем только разрешенные поля
            update_data = order_data.model_dump(exclude_unset=True)
            updated_order = await db.order_repo.update(order_id, **update_data)
            
            await db.commit()
            return updated_order
    
    @staticmethod
    async def cancel_order(order_id: int, user_id: int) -> bool:
        async with TransactionDbManager() as db:
            # Проверяем, что заказ существует и принадлежит пользователю
            order = await db.order_repo.get_by_id(order_id)
            
            if not order or order.user_id != user_id:
                return False
            
            # Нельзя отменить заказ, который уже в работе или доставлен
            if order.status not in [OrderStatus.PENDING, OrderStatus.ACCEPTED]:
                raise ValueError(f"Cannot cancel order with status {order.status}")
            
            cancelled_order = await db.order_repo.cancel_order(order_id, user_id)
            
            # Если заказ был принят водителем, освобождаем его
            if cancelled_order and cancelled_order.driver_id:
                await db.driver_repo.update_status(cancelled_order.driver_id, "available")
            
            await db.commit()
            return cancelled_order is not None
    
    @staticmethod
    async def accept_order(order_id: int, driver_id: int) -> dict | None:
        async with TransactionDbManager() as db:
            # Проверяем, что водитель существует и доступен
            driver = await db.driver_repo.get_by_id(driver_id)
            
            if not driver or driver.status != "available" or not driver.is_active:
                raise ValueError("Driver not available")
            
            # Проверяем, что заказ существует и в статусе PENDING
            order = await db.order_repo.get_by_id(order_id)
            
            if not order or order.status != OrderStatus.PENDING:
                raise ValueError("Order not available for acceptance")
            
            # Принимаем заказ
            accepted_order = await db.order_repo.accept_order(order_id, driver_id)
            
            if accepted_order:
                # Обновляем статус водителя
                await db.driver_repo.update_status(driver_id, "busy")
                await db.commit()
                
                return {
                    "order": accepted_order,
                    "driver": driver
                }
            
            return None
    
    @staticmethod
    async def decline_order(order_id: int, driver_id: int) -> bool:
        async with TransactionDbManager() as db:
            # Проверяем, что заказ принят этим водителем
            order = await db.order_repo.get_by_id(order_id)
            
            if not order or order.driver_id != driver_id or order.status != OrderStatus.ACCEPTED:
                return False
            
            # Отменяем принятие заказа
            updated_order = await db.order_repo.update_order_status(order_id, OrderStatus.PENDING)
            
            if updated_order:
                # Освобождаем водителя
                await db.driver_repo.update_status(driver_id, "available")
                await db.commit()
                return True
            
            return False
    
    @staticmethod
    async def update_order_status(order_id: int, driver_id: int, status: OrderStatus) -> dict | None:
        async with TransactionDbManager() as db:
            # Проверяем, что заказ принадлежит водителю
            order = await db.order_repo.get_by_id(order_id)
            
            if not order or order.driver_id != driver_id:
                return None
            
            # Валидация перехода статусов
            valid_transitions = {
                OrderStatus.ACCEPTED: [OrderStatus.PICKED_UP, OrderStatus.CANCELLED],
                OrderStatus.PICKED_UP: [OrderStatus.IN_TRANSIT],
                OrderStatus.IN_TRANSIT: [OrderStatus.DELIVERED]
            }
            
            if status not in valid_transitions.get(order.status, []):
                raise ValueError(f"Invalid status transition from {order.status} to {status}")
            
            # Обновляем статус
            updated_order = await db.order_repo.update_order_status(order_id, status, driver_id)
            
            # Если заказ доставлен, освобождаем водителя
            if status == OrderStatus.DELIVERED:
                await db.driver_repo.update_status(driver_id, "available")
            
            await db.commit()
            return updated_order