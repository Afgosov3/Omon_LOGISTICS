from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User, UserRole
from audit.models import AuditLog
from clients.models import Client
from drivers.models import Driver
from notifications.models import Notification, TargetType, Channel
from orders.models import (
    Order,
    OrderPoint,
    OrderPointType,
    OrderStatus,
    OrderStatusHistory,
)
from payouts.models import Payout, PayoutStatus, PaymentMethod
from telegram_bot.models import BotSession
from vehicles.models import Vehicle


class Command(BaseCommand):
    help = "Seed the database with demo data for local testing (at least 3 rows per model)."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creating demo data…")

        users = self._create_users()
        clients = self._create_clients(users)
        drivers = self._create_drivers(users)
        vehicles = self._create_vehicles(drivers)
        orders = self._create_orders(users, clients, drivers, vehicles)
        self._create_order_points(orders)
        self._create_status_history(orders, users, drivers)
        self._create_payouts(orders, drivers, users)
        self._create_notifications(clients, drivers, users, orders)
        self._create_bot_sessions(drivers, clients)
        self._create_audit_logs(users, clients, drivers)

        self.stdout.write(self.style.SUCCESS("Demo data created/ensured."))

    def _create_users(self):
        user_specs = [
            {
                "email": "main.dispatcher@example.com",
                "username": "main_dispatcher",
                "phone": "+998900000001",
                "role": UserRole.MAIN_DISPATCHER,
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "email": "dispatcher.one@example.com",
                "username": "dispatcher1",
                "phone": "+998900000002",
                "role": UserRole.DISPATCHER,
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "email": "dispatcher.two@example.com",
                "username": "dispatcher2",
                "phone": "+998900000003",
                "role": UserRole.DISPATCHER,
                "is_staff": True,
                "is_superuser": False,
            },
        ]

        users = []
        for spec in user_specs:
            user, created = User.objects.get_or_create(
                email=spec["email"],
                defaults={
                    "username": spec["username"],
                    "role": spec["role"],
                    "phone": spec["phone"],
                    "is_staff": spec["is_staff"],
                    "is_superuser": spec["is_superuser"],
                },
            )
            if created:
                user.set_password("demo12345")
                user.save()
            users.append(user)
        return users

    def _create_clients(self, users):
        client_specs = [
            {
                "full_name": "Ali Valiyev",
                "company_name": "Ali Logistics LLC",
                "phone": "+998901111111",
                "email": "ali@example.com",
                "address": "Tashkent, Yunusabad",
                "telegram_id": 700000001,
                "telegram_username": "ali_client",
                "language": "uz",
                "created_by": users[0],
            },
            {
                "full_name": "Bobur Karimov",
                "company_name": "BK Transport",
                "phone": "+998902222222",
                "email": "bobur@example.com",
                "address": "Samarkand, Registan",
                "telegram_id": 700000002,
                "telegram_username": "bobur_client",
                "language": "ru",
                "created_by": users[1],
            },
            {
                "full_name": "Dilorom Xujaeva",
                "company_name": "DX Trade",
                "phone": "+998903333333",
                "email": "dilorom@example.com",
                "address": "Bukhara, Old Town",
                "telegram_id": 700000003,
                "telegram_username": "dilorom_client",
                "language": "en",
                "created_by": users[2],
            },
        ]
        clients = []
        for spec in client_specs:
            client, _ = Client.objects.get_or_create(
                phone=spec["phone"],
                defaults={**spec, "notes": "Demo client", "is_active": True},
            )
            clients.append(client)
        return clients

    def _create_drivers(self, users):
        driver_specs = [
            {
                "full_name": "Aziz Turayev",
                "phone": "+998941111111",
                "telegram_id": 800000001,
                "telegram_username": "aziz_driver",
                "card_holder_name": "Aziz T",
                "card_mask": "8600 **** 1234",
                "card_last4": "1234",
                "created_by": users[0],
                "current_lat": Decimal("41.2995"),
                "current_lng": Decimal("69.2401"),
            },
            {
                "full_name": "Bekzod Rustamov",
                "phone": "+998942222222",
                "telegram_id": 800000002,
                "telegram_username": "bekzod_driver",
                "card_holder_name": "Bekzod R",
                "card_mask": "9860 **** 5678",
                "card_last4": "5678",
                "created_by": users[1],
                "current_lat": Decimal("39.6542"),
                "current_lng": Decimal("66.9597"),
            },
            {
                "full_name": "Jasur Otabekov",
                "phone": "+998943333333",
                "telegram_id": 800000003,
                "telegram_username": "jasur_driver",
                "card_holder_name": "Jasur O",
                "card_mask": "5440 **** 9012",
                "card_last4": "9012",
                "created_by": users[2],
                "current_lat": Decimal("40.1039"),
                "current_lng": Decimal("65.3688"),
            },
        ]
        drivers = []
        now = timezone.now()
        for spec in driver_specs:
            driver, _ = Driver.objects.get_or_create(
                telegram_id=spec["telegram_id"],
                defaults={
                    **spec,
                    "is_active": True,
                    "is_online": True,
                    "joined_at": now,
                    "notes": "Demo driver",
                    "last_location_update": now,
                },
            )
            drivers.append(driver)
        return drivers

    def _create_vehicles(self, drivers):
        vehicle_specs = [
            {
                "driver": drivers[0],
                "type": "truck",
                "brand": "MAN",
                "model": "TGX",
                "plate_number": "01 A 111 AA",
                "capacity_kg": Decimal("20000"),
                "volume_m3": Decimal("45.5"),
            },
            {
                "driver": drivers[1],
                "type": "van",
                "brand": "Mercedes",
                "model": "Sprinter",
                "plate_number": "50 B 222 BB",
                "capacity_kg": Decimal("3500"),
                "volume_m3": Decimal("18.0"),
            },
            {
                "driver": drivers[2],
                "type": "pickup",
                "brand": "Isuzu",
                "model": "D-MAX",
                "plate_number": "80 C 333 CC",
                "capacity_kg": Decimal("1500"),
                "volume_m3": Decimal("8.0"),
            },
        ]
        vehicles = []
        for spec in vehicle_specs:
            vehicle, _ = Vehicle.objects.get_or_create(
                plate_number=spec["plate_number"],
                defaults={**spec, "is_active": True},
            )
            vehicles.append(vehicle)
        return vehicles

    def _create_orders(self, users, clients, drivers, vehicles):
        order_specs = [
            {
                "public_id": "DEMO-ORDER-1",
                "client": clients[0],
                "created_by_dispatcher": users[0],
                "assigned_dispatcher": users[0],
                "assigned_driver": drivers[0],
                "assigned_vehicle": vehicles[0],
                "cargo_name": "Electronics",
                "cargo_description": "Laptops and accessories",
                "cargo_weight_kg": Decimal("1200.50"),
                "cargo_volume_m3": Decimal("9.5"),
                "cargo_category": "Electronics",
                "client_price": Decimal("15000"),
                "driver_price": Decimal("11000"),
                "current_status": OrderStatus.DRIVER_ASSIGNED,
                "internal_comment": "High priority",
                "assigned_at": timezone.now(),
                "driver_assigned_at": timezone.now(),
                "estimated_distance_km": 350.5,
                "estimated_duration_minutes": 420,
            },
            {
                "public_id": "DEMO-ORDER-2",
                "client": clients[1],
                "created_by_dispatcher": users[1],
                "assigned_dispatcher": users[1],
                "assigned_driver": drivers[1],
                "assigned_vehicle": vehicles[1],
                "cargo_name": "Textiles",
                "cargo_description": "Cotton rolls",
                "cargo_weight_kg": Decimal("8000"),
                "cargo_volume_m3": Decimal("30.0"),
                "cargo_category": "Textile",
                "client_price": Decimal("22000"),
                "driver_price": Decimal("17000"),
                "current_status": OrderStatus.ON_THE_WAY_WITH_CARGO,
                "internal_comment": "Requires tarp",
                "assigned_at": timezone.now(),
                "driver_assigned_at": timezone.now(),
                "estimated_distance_km": 520.0,
                "estimated_duration_minutes": 600,
            },
            {
                "public_id": "DEMO-ORDER-3",
                "client": clients[2],
                "created_by_dispatcher": users[2],
                "assigned_dispatcher": users[2],
                "assigned_driver": drivers[2],
                "assigned_vehicle": vehicles[2],
                "cargo_name": "Food products",
                "cargo_description": "Frozen goods",
                "cargo_weight_kg": Decimal("3000"),
                "cargo_volume_m3": Decimal("12.0"),
                "cargo_category": "Food",
                "client_price": Decimal("18000"),
                "driver_price": Decimal("13000"),
                "current_status": OrderStatus.CLIENT_CONFIRMED,
                "internal_comment": "Keep cold chain",
                "assigned_at": timezone.now(),
                "driver_assigned_at": timezone.now(),
                "estimated_distance_km": 200.0,
                "estimated_duration_minutes": 240,
            },
        ]
        orders = []
        for spec in order_specs:
            order, _ = Order.objects.get_or_create(
                public_id=spec["public_id"],
                defaults=spec,
            )
            orders.append(order)
        return orders

    def _create_order_points(self, orders):
        for idx, order in enumerate(orders, start=1):
            OrderPoint.objects.get_or_create(
                order=order,
                sequence=1,
                defaults={
                    "point_type": OrderPointType.PICKUP,
                    "address": f"Pickup address {idx}",
                    "latitude": Decimal("41.000000"),
                    "longitude": Decimal("69.000000"),
                    "contact_person": "Pickup Person",
                    "contact_phone": "+998900000010",
                },
            )
            OrderPoint.objects.get_or_create(
                order=order,
                sequence=2,
                defaults={
                    "point_type": OrderPointType.DROPOFF,
                    "address": f"Dropoff address {idx}",
                    "latitude": Decimal("40.500000"),
                    "longitude": Decimal("68.500000"),
                    "contact_person": "Dropoff Person",
                    "contact_phone": "+998900000020",
                },
            )

    def _create_status_history(self, orders, users, drivers):
        for order in orders:
            OrderStatusHistory.objects.get_or_create(
                order=order,
                new_status=OrderStatus.CLIENT_CONFIRMED,
                defaults={
                    "old_status": OrderStatus.NEW,
                    "changed_by_user": users[0],
                    "changed_by_driver": None,
                    "changed_by_system": False,
                    "actor_role": "dispatcher",
                    "comment": "Client confirmed",
                },
            )
            OrderStatusHistory.objects.get_or_create(
                order=order,
                new_status=OrderStatus.DRIVER_ASSIGNED,
                defaults={
                    "old_status": OrderStatus.CLIENT_CONFIRMED,
                    "changed_by_user": users[0],
                    "changed_by_driver": drivers[0],
                    "changed_by_system": False,
                    "actor_role": "dispatcher",
                    "comment": "Driver assigned",
                },
            )

    def _create_payouts(self, orders, drivers, users):
        for idx, order in enumerate(orders):
            driver = drivers[idx % len(drivers)]
            Payout.objects.get_or_create(
                order=order,
                defaults={
                    "driver": driver,
                    "amount": order.driver_price,
                    "status": PayoutStatus.PAID if idx % 2 == 0 else PayoutStatus.PENDING,
                    "payment_method": PaymentMethod.BANK_TRANSFER,
                    "paid_by_user": users[0],
                    "paid_at": timezone.now() if idx % 2 == 0 else None,
                    "card_mask": driver.card_mask,
                    "comment": "Demo payout",
                },
            )

    def _create_notifications(self, clients, drivers, users, orders):
        Notification.objects.get_or_create(
            target_type=TargetType.CLIENT,
            target_id=clients[0].id,
            channel=Channel.TELEGRAM,
            defaults={
                "title": "New order created",
                "body": "Siz uchun yangi buyurtma yaratildi",
                "related_order_id": orders[0].id,
                "is_read": False,
                "sent_at": timezone.now(),
            },
        )
        Notification.objects.get_or_create(
            target_type=TargetType.DRIVER,
            target_id=drivers[0].id,
            channel=Channel.TELEGRAM,
            defaults={
                "title": "Yuk tayyor",
                "body": "Yukni olib ketish uchun jo'nang",
                "related_order_id": orders[0].id,
                "is_read": False,
                "sent_at": timezone.now(),
            },
        )
        Notification.objects.get_or_create(
            target_type=TargetType.USER,
            target_id=users[0].id,
            channel=Channel.CRM,
            defaults={
                "title": "Dashboard update",
                "body": "3 ta yangi buyurtma qo'shildi",
                "related_order_id": orders[1].id,
                "is_read": True,
                "sent_at": timezone.now(),
            },
        )

    def _create_bot_sessions(self, drivers, clients):
        BotSession.objects.get_or_create(
            telegram_id=drivers[0].telegram_id,
            defaults={"role": "driver", "state": "idle", "payload_json": {"demo": True}},
        )
        BotSession.objects.get_or_create(
            telegram_id=clients[0].telegram_id,
            defaults={"role": "client", "state": "idle", "payload_json": {"demo": True}},
        )
        BotSession.objects.get_or_create(
            telegram_id=999999999,
            defaults={"role": "dispatcher", "state": "idle", "payload_json": {"demo": True}},
        )

    def _create_audit_logs(self, users, clients, drivers):
        AuditLog.objects.get_or_create(
            action="user_login",
            entity_type="user",
            entity_id=users[0].id,
            defaults={
                "actor_type": "user",
                "actor_id": users[0].id,
                "before_json": None,
                "after_json": {"role": users[0].role},
                "ip_address": "127.0.0.1",
                "user_agent": "demo-agent",
            },
        )
        AuditLog.objects.get_or_create(
            action="client_created",
            entity_type="client",
            entity_id=clients[0].id,
            defaults={
                "actor_type": "user",
                "actor_id": users[0].id,
                "before_json": None,
                "after_json": {"client": clients[0].full_name},
                "ip_address": "127.0.0.1",
                "user_agent": "demo-agent",
            },
        )
        AuditLog.objects.get_or_create(
            action="driver_location_update",
            entity_type="driver",
            entity_id=drivers[0].id,
            defaults={
                "actor_type": "driver",
                "actor_id": drivers[0].id,
                "before_json": None,
                "after_json": {
                    "lat": str(drivers[0].current_lat or ""),
                    "lng": str(drivers[0].current_lng or ""),
                },
                "ip_address": "127.0.0.1",
                "user_agent": "demo-agent",
            },
        )

