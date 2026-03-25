from aiogram import Router, F
from aiogram.types import CallbackQuery
from telegram_bot.services import BotService
from telegram_bot.keyboards.keyboards import (
    get_customer_main_keyboard,
    get_order_list_keyboard,
    get_customer_order_actions_keyboard
)

router = Router()

@router.callback_query(F.data == "customer_orders")
async def show_customer_orders(call: CallbackQuery):
    client = await BotService.get_customer_by_telegram_id(call.from_user.id)
    if not client:
        await call.answer("Mijoz topilmadi!", show_alert=True)
        return

    orders = await BotService.get_customer_orders(client)
    if not orders:
        await call.message.edit_text("Sizda faol buyurtmalar yo'q.", reply_markup=get_customer_main_keyboard())
    else:
        await call.message.edit_text("Buyurtmangizni tanlang:", reply_markup=get_order_list_keyboard(orders, "customer"))

@router.callback_query(F.data.startswith("order_detail_customer_"))
async def show_order_detail_customer(call: CallbackQuery):
    order_id = int(call.data.split("_")[-1])
    order = await BotService.get_order_by_id(order_id)

    if not order:
        await call.answer("Buyurtma topilmadi!", show_alert=True)
        return

    pickup = await BotService.get_pickup_point(order)
    dropoff = await BotService.get_dropoff_point(order)
    pickup_addr = pickup.address if pickup else "Noma'lum"
    dropoff_addr = dropoff.address if dropoff else "Noma'lum"

    driver_name = "Biriktirilmagan"
    vehicle_info = ""

    if order.assigned_driver:
        driver_name = order.assigned_driver.full_name
        if order.assigned_vehicle:
             vehicle_info = f"({order.assigned_vehicle.plate_number})"

    price = order.client_price if order.client_price else 0

    text = f"📦 Buyurtma #{order.public_id[-6:]}\n\n" \
           f"📍 Olish: {pickup_addr}\n" \
           f"🏁 Tushirish: {dropoff_addr}\n" \
           f"💰 Narx: {price:,.0f} so'm\n" \
           f"🚚 Haydovchi: {driver_name} {vehicle_info}\n" \
           f"🔄 Status: {order.get_current_status_display()}\n"

    await call.message.edit_text(text, reply_markup=get_customer_order_actions_keyboard(order.id))

@router.callback_query(F.data.startswith("track_order_"))
async def track_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[-1])
    order = await BotService.get_order_by_id(order_id)

    if not order or not order.assigned_driver:
        await call.answer("Haydovchi topilmadi yoki buyurtma yo'q.", show_alert=True)
        return

    # Assuming we added Lat/Long to Driver model
    lat = order.assigned_driver.current_lat
    lon = order.assigned_driver.current_long
    last_seen = order.assigned_driver.last_location_at

    if lat and lon:
         await call.message.answer_location(latitude=float(lat), longitude=float(lon))
         time_str = last_seen.strftime('%H:%M') if last_seen else ""
         await call.message.answer(f"Haydovchi so'nggi lokatsiyasi ({time_str}): https://maps.google.com/?q={lat},{lon}")
    else:
         await call.answer("Haydovchi lokatsiyasi mavjud emas.", show_alert=True)

