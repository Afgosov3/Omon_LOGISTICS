from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone
from clients.models import Client
from drivers.models import Driver
from orders.models import Order, OrderStatus, OrderPoint, OrderPointType
from orders.services import OrderService
from aiogram import Bot
import os

class BotService:
    @staticmethod
    async def send_message(telegram_id, text):
        token = os.getenv("BOT_TOKEN")
        if not token or not telegram_id:
            return

        try:
            bot = Bot(token=token)
            await bot.send_message(chat_id=telegram_id, text=text)
            await bot.session.close()
        except Exception as e:
            print(f"Failed to send message to {telegram_id}: {e}")

    @staticmethod
    async def get_driver_by_telegram_id(telegram_id):
        try:
            return await Driver.objects.aget(telegram_id=telegram_id)
        except Driver.DoesNotExist:
            return None

    @staticmethod
    async def get_customer_by_telegram_id(telegram_id):
        try:
            return await Client.objects.aget(telegram_id=telegram_id)
        except Client.DoesNotExist:
            return None

    @staticmethod
    async def register_user(telegram_id, phone, full_name):
        phone = phone.replace("+", "").replace(" ", "")

        driver = await Driver.objects.filter(phone__contains=phone[-9:]).afirst()
        if driver:
            driver.telegram_id = telegram_id
            await driver.asave()
            return "driver", driver

        client = await Client.objects.filter(phone__contains=phone[-9:]).afirst()
        if client:
            client.telegram_id = telegram_id
            client.telegram_username = full_name # Optional
            await client.asave()
            return "customer", client

        return None, None

    @staticmethod
    @sync_to_async
    def get_driver_orders(driver):
        return list(Order.objects.filter(
            assigned_driver=driver
        ).exclude(
            current_status__in=[OrderStatus.COMPLETED, OrderStatus.CANCELLED]
        ).select_related('client').prefetch_related('points').order_by('-created_at'))

    @staticmethod
    @sync_to_async
    def get_customer_orders(client):
        return list(Order.objects.filter(
            client=client
        ).exclude(
            current_status__in=[OrderStatus.COMPLETED, OrderStatus.CANCELLED]
        ).select_related('assigned_driver').prefetch_related('points').order_by('-created_at'))

    @staticmethod
    @sync_to_async
    def get_order_by_id(order_id):
        try:
            return Order.objects.select_related(
                'assigned_driver', 'client', 'assigned_vehicle'
            ).prefetch_related('points').get(id=order_id)
        except Order.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def get_order_for_driver(order_id, driver):
        try:
            return Order.objects.select_related(
                'assigned_driver', 'client', 'assigned_vehicle'
            ).prefetch_related('points').get(id=order_id, assigned_driver=driver)
        except Order.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def get_order_for_customer(order_id, client):
        try:
            return Order.objects.select_related(
                'assigned_driver', 'client', 'assigned_vehicle'
            ).prefetch_related('points').get(id=order_id, client=client)
        except Order.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def update_order_status(order_id, new_status, driver=None, proof_file=None, proof_type=None):
        try:
            order = Order.objects.select_related('assigned_driver').get(id=order_id)
            if driver and order.assigned_driver_id != driver.id:
                return None
            return OrderService.update_status(
                order=order,
                new_status=new_status,
                driver=driver,
                proof_file=proof_file,
                proof_type=proof_type
            )
        except Exception as e:
            print(f"Error updating status: {e}")
            return None

    @staticmethod
    async def update_driver_location(driver_id, lat, lon):
        try:
            driver = await Driver.objects.aget(id=driver_id)
            driver.current_lat = lat
            driver.current_lng = lon
            driver.last_location_update = timezone.now()
            await driver.asave(update_fields=["current_lat", "current_lng", "last_location_update"])
        except Driver.DoesNotExist:
            pass

    @staticmethod
    @sync_to_async
    def get_pickup_point(order):
        return order.points.filter(point_type=OrderPointType.PICKUP).first()

    @staticmethod
    @sync_to_async
    def get_dropoff_point(order):
        return order.points.filter(point_type=OrderPointType.DROPOFF).last()
