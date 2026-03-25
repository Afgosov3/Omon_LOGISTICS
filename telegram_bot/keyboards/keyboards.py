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
            [InlineKeyboardButton(text="📍 Lokatsiya yuborish", callback_data="driver_location")],
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
    buttons = []

    # Status mapping:
    # DRIVER_ASSIGNED -> ON_THE_WAY_TO_PICKUP
    # ON_THE_WAY_TO_PICKUP -> AT_PICKUP_LOCATION
    # AT_PICKUP_LOCATION -> LOADED (Proof)
    # LOADED -> ON_THE_WAY_WITH_CARGO
    # ON_THE_WAY_WITH_CARGO -> AT_DROPOFF_LOCATION
    # AT_DROPOFF_LOCATION -> UNLOADING_CONFIRMED (Proof)

    if current_status == OrderStatus.DRIVER_ASSIGNED:
        buttons.append([InlineKeyboardButton(text="🚚 Yo'lga chiqdim (Yuk olishga)", callback_data=f"status_{order_id}_on_way_to_pickup")])
    elif current_status == OrderStatus.ON_THE_WAY_TO_PICKUP:
        buttons.append([InlineKeyboardButton(text="📍 Yetib keldim (Yuk olishga)", callback_data=f"status_{order_id}_at_pickup_location")])
    elif current_status == OrderStatus.AT_PICKUP_LOCATION:
        buttons.append([InlineKeyboardButton(text="📦 Yuklandi (Proof)", callback_data=f"proof_request_{order_id}_loaded")])
    elif current_status == OrderStatus.LOADED:
        buttons.append([InlineKeyboardButton(text="🚚 Yo'lga chiqdim (Yuk bilan)", callback_data=f"status_{order_id}_on_the_way_with_cargo")])
    elif current_status == OrderStatus.ON_THE_WAY_WITH_CARGO:
        buttons.append([InlineKeyboardButton(text="📍 Yetib keldim (Tushirishga)", callback_data=f"status_{order_id}_at_dropoff_location")])
    elif current_status == OrderStatus.AT_DROPOFF_LOCATION:
        buttons.append([InlineKeyboardButton(text="✅ Yakunlash (Proof)", callback_data=f"proof_request_{order_id}_unloading_confirmed")])
    # For UNLOADING_CONFIRMED -> COMPLETED, usually dispatcher does it, but driver can request completion or similar.
    # Currently no action for driver here.

    buttons.append([InlineKeyboardButton(text="📍 Lokatsiya yuborish", callback_data=f"send_loc_{order_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="driver_orders")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_customer_order_actions_keyboard(order_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚚 Yuk qayerda?", callback_data=f"track_order_{order_id}")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="customer_orders")]
        ]
    )

def get_back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_home")]
        ]
    )

