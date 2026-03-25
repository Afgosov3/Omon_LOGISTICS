from django.db import transaction
from django.utils import timezone
from .models import Order, OrderStatus, OrderProof, OrderStatusHistory, OrderPoint
from drivers.models import Driver
from notifications.models import Notification, TargetType, Channel


class OrderService:
    @staticmethod
    @transaction.atomic
    def assign_driver(order_id, driver, user=None):
        order = Order.objects.get(pk=order_id)

        old_status = order.current_status
        order.assigned_driver = driver
        order.current_status = OrderStatus.DRIVER_ASSIGNED
        order.driver_assigned_at = timezone.now()
        order.save()

        # History
        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=OrderStatus.DRIVER_ASSIGNED,
            changed_by_user=user,
            comment=f"Assigned to driver {driver.full_name}" if user else f"Assigned to driver {driver.full_name}"
        )

        # Notify Driver
        if driver.telegram_id:
            OrderService._create_notification(
                target_type=TargetType.DRIVER,
                target_id=driver.id,
                title="Yangi buyurtma!",
                body=f"Sizga yangi buyurtma biriktirildi: {order.public_id}",
                channel=Channel.TELEGRAM,
                order_id=order.id
            )

        return order

    @staticmethod
    def _create_notification(target_type, target_id, title, body, channel=Channel.CRM, order_id=None):
        Notification.objects.create(
            target_type=target_type,
            target_id=target_id,
            title=title,
            body=body,
            channel=channel,
            related_order_id=order_id,
        )

    @staticmethod
    @transaction.atomic
    def update_status(order, new_status, user=None, driver=None, comment="", proof_file=None, proof_type=None):
        old_status = order.current_status

        if old_status == new_status:
            return order

        order.current_status = new_status
        if new_status == OrderStatus.COMPLETED:
            order.completed_at = timezone.now()

        order.save()

        history = OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by_user=user,
            changed_by_driver=driver,
            comment=comment
        )

        if proof_file and proof_type:
            proof = OrderProof.objects.create(
                order=order,
                status_history=history,
                uploaded_by_user=user,
                uploaded_by_driver=driver,
                file=proof_file,
                proof_kind=proof_type,
                comment=comment
            )

        # Notify Client about status change
        if order.client and order.client.telegram_id:
             msg = f"Buyurtma statusi o'zgardi: {order.get_current_status_display()}"
             OrderService._create_notification(
                target_type=TargetType.CLIENT,
                target_id=order.client.id,
                title="Status o'zgardi",
                body=msg,
                channel=Channel.TELEGRAM,
                order_id=order.id
             )

        return order

