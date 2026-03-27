from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from telegram_bot.services import BotService
from telegram_bot.keyboards.keyboards import (
    get_customer_main_keyboard,
    get_order_list_keyboard,
    get_customer_order_actions_keyboard
)

router = Router()

async def safe_edit_text(message, text, reply_markup=None):
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        raise

@router.callback_query(F.data == "customer_orders")
async def show_customer_orders(call: CallbackQuery):
    client = await BotService.get_customer_by_telegram_id(call.from_user.id)
    if not client:
        await call.answer("Mijoz topilmadi!", show_alert=True)
        return

    orders = await BotService.get_customer_orders(client)
    if not orders:
        await safe_edit_text(call.message, "Sizda faol buyurtmalar yo'q.", reply_markup=get_customer_main_keyboard())
    else:
        await safe_edit_text(call.message, "Buyurtmangizni tanlang:", reply_markup=get_order_list_keyboard(orders, "customer"))

@router.callback_query(F.data.startswith("order_detail_customer_"))
async def show_order_detail_customer(call: CallbackQuery):
    order_id = int(call.data.split("_")[-1])
    client = await BotService.get_customer_by_telegram_id(call.from_user.id)

    if not client:
        await call.answer("Mijoz topilmadi!", show_alert=True)
        return

    order = await BotService.get_order_for_customer(order_id, client)

    if not order:
        await call.answer("Buyurtma topilmadi!", show_alert=True)
        return

    pickup = await BotService.get_pickup_point(order)
    dropoff = await BotService.get_dropoff_point(order)
    pickup_addr = pickup.address if pickup else "Noma'lum"
    dropoff_addr = dropoff.address if dropoff else "Noma'lum"

    price = order.client_price if order.client_price else 0

    text = f"📦 Buyurtma #{order.public_id[-6:]}\n\n" \
           f"📍 Olish: {pickup_addr}\n" \
           f"🏁 Tushirish: {dropoff_addr}\n" \
           f"💰 Narx: {price:,.0f} so'm\n" \
           f"🔄 Status: {order.get_current_status_display()}\n"

    await safe_edit_text(call.message, text, reply_markup=get_customer_order_actions_keyboard(order.id))

@router.callback_query(F.data.startswith("track_order_"))
async def track_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[-1])
    client = await BotService.get_customer_by_telegram_id(call.from_user.id)
    order = await BotService.get_order_for_customer(order_id, client) if client else None

    if not order:
        await call.answer("Buyurtma topilmadi", show_alert=True)
        return

    driver = order.assigned_driver
    if not driver:
        await call.answer("Haydovchi biriktirilmagan", show_alert=True)
        return

    lat = driver.current_lat
    lng = driver.current_lng
    updated_at = driver.last_location_update

    if lat is None or lng is None:
        if driver.telegram_id:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📍 Lokatsiyani yuborish", callback_data=f"send_loc_{order.id}")]
            ])
            await BotService.send_message(
                driver.telegram_id,
                "Mijoz lokatsiya so'radi. Iltimos, lokatsiyani yuboring.",
                reply_markup=kb,
            )
            await call.answer("Haydovchidan lokatsiya so'raldi.", show_alert=True)
        else:
            await call.answer("Haydovchi Telegram bilan bog'lanmagan.", show_alert=True)
        return

    await call.message.answer_location(latitude=float(lat), longitude=float(lng))
    if updated_at:
        await call.message.answer(f"Oxirgi yangilanish: {updated_at.strftime('%Y-%m-%d %H:%M')}")
    await call.answer()
