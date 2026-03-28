from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from orders.models import OrderStatus, OrderPointType

def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamini yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_driver_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Mening buyurtmalarim", callback_data="driver_orders")],
        ]
    )

def get_customer_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Mening buyurtmalarim", callback_data="customer_orders")],
        ]
    )

def get_order_list_keyboard(orders, role="driver"):
    buttons = []
    for order in orders:
        # Assuming points are prefetched or loaded
        points = getattr(order, 'points_list', list(order.points.all()))

        pickup = next((p for p in points if p.point_type == OrderPointType.PICKUP), None)
        dropoff = next((p for p in points if p.point_type == OrderPointType.DROPOFF), None)

        pickup_addr = pickup.address[:15] + ".." if pickup and len(pickup.address) > 15 else (pickup.address if pickup else "???")
        dropoff_addr = dropoff.address[:15] + ".." if dropoff and len(dropoff.address) > 15 else (dropoff.address if dropoff else "???")

        text = f"#{order.public_id[-4:]} {pickup_addr} -> {dropoff_addr}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"order_detail_{role}_{order.id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_driver_order_actions_keyboard(order_id, current_status):
    buttons = [
        [InlineKeyboardButton(text="🔄 Statusni o'zgartirish", callback_data=f"status_menu_{order_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="driver_orders")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_driver_status_change_keyboard(order_id, current_status):
    status_options = {
        "on_way_to_pickup": (OrderStatus.ON_THE_WAY_TO_PICKUP, "🚚 Yo'lga chiqdim (yuk olishga)", False),
        "at_pickup_location": (OrderStatus.AT_PICKUP_LOCATION, "📍 Yetib keldim (yuk olishga)", False),
        "loaded": (OrderStatus.LOADED, "📦 Yuklandi (video)", True),
        "on_the_way_with_cargo": (OrderStatus.ON_THE_WAY_WITH_CARGO, "🚚 Yo'lga chiqdim (yuk bilan)", False),
        "at_dropoff_location": (OrderStatus.AT_DROPOFF_LOCATION, "📍 Yetib keldim (tushirishga)", False),
        "unloading_requested": (OrderStatus.UNLOADING_REQUESTED, "📦 Tushirishni boshladim (video)", True),
        "unloading_confirmed": (OrderStatus.UNLOADING_CONFIRMED, "✅ Tushirish tugadi (video)", True),
        "completed": (OrderStatus.COMPLETED, "✅ Buyurtma yakunlandi", False),
    }

    allowed_by_status = {
        OrderStatus.DRIVER_ASSIGNED: ["on_way_to_pickup"],
        OrderStatus.ON_THE_WAY_TO_PICKUP: ["at_pickup_location"],
        OrderStatus.AT_PICKUP_LOCATION: ["loaded"],
        OrderStatus.LOADED: ["on_the_way_with_cargo"],
        OrderStatus.ON_THE_WAY_WITH_CARGO: ["at_dropoff_location"],
        OrderStatus.AT_DROPOFF_LOCATION: ["unloading_requested"],
        OrderStatus.UNLOADING_REQUESTED: ["unloading_confirmed"],
        OrderStatus.UNLOADING_CONFIRMED: ["completed"],
        # Allow drivers to start the chain even if status is still in early dispatcher stages
        OrderStatus.CLIENT_CONFIRMED: ["on_way_to_pickup"],
        OrderStatus.DRIVER_SEARCH: ["on_way_to_pickup"],
        OrderStatus.NEW: ["on_way_to_pickup"],
    }

    # Normalize the status so lookups work even if a raw string is passed in
    try:
        status_key = OrderStatus(current_status)
    except Exception:
        status_key = current_status

    buttons = []
    next_codes = allowed_by_status.get(status_key, [])
    # Fallback: if nothing matched, still offer the first leg to keep UX unblocked
    if not next_codes:
        next_codes = allowed_by_status.get(OrderStatus.DRIVER_ASSIGNED, [])

    for code in next_codes:
        _, label, requires_video = status_options[code]
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"status_pick_{order_id}_{code}")])

    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"order_detail_driver_{order_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_customer_order_actions_keyboard(order_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📍 Buyurtmam qayerda?", callback_data=f"track_order_{order_id}")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="customer_orders")]
        ]
    )

def get_back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_home")]
        ]
    )
