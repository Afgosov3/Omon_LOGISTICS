from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from telegram_bot.services import BotService
from telegram_bot.keyboards.keyboards import (
    get_driver_main_keyboard,
    get_order_list_keyboard,
    get_driver_order_actions_keyboard,
    get_back_keyboard,
    get_customer_main_keyboard,
    get_driver_status_change_keyboard,
)
from telegram_bot.states.states import DriverOrderState
from orders.models import OrderStatus, ProofKind
from django.core.files.base import ContentFile
from django.conf import settings
import io
import re

router = Router()

STATUS_PICK_RE = re.compile(r"^status_pick_(\d+)_(.+)$")
STATUS_MENU_RE = re.compile(r"^status_menu_(\d+)$")

async def safe_edit_text(message, text, reply_markup=None):
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        raise

STATUS_OPTION_MAP = {
    "on_way_to_pickup": (OrderStatus.ON_THE_WAY_TO_PICKUP, False),
    "at_pickup_location": (OrderStatus.AT_PICKUP_LOCATION, False),
    "loaded": (OrderStatus.LOADED, True),
    "on_the_way_with_cargo": (OrderStatus.ON_THE_WAY_WITH_CARGO, False),
    "at_dropoff_location": (OrderStatus.AT_DROPOFF_LOCATION, False),
    "unloading_requested": (OrderStatus.UNLOADING_REQUESTED, True),
    "unloading_confirmed": (OrderStatus.UNLOADING_CONFIRMED, True),
    "completed": (OrderStatus.COMPLETED, False),
}

ALLOWED_STATUS_BY_CURRENT = {
    OrderStatus.DRIVER_ASSIGNED: ["on_way_to_pickup"],
    OrderStatus.ON_THE_WAY_TO_PICKUP: ["at_pickup_location"],
    OrderStatus.AT_PICKUP_LOCATION: ["loaded"],
    OrderStatus.LOADED: ["on_the_way_with_cargo"],
    OrderStatus.ON_THE_WAY_WITH_CARGO: ["at_dropoff_location"],
    OrderStatus.AT_DROPOFF_LOCATION: ["unloading_requested"],
    OrderStatus.UNLOADING_REQUESTED: ["unloading_confirmed"],
    OrderStatus.UNLOADING_CONFIRMED: ["completed"],
    # allow driver to start even if order is still early-stage
    OrderStatus.NEW: ["on_way_to_pickup"],
    OrderStatus.DRIVER_SEARCH: ["on_way_to_pickup"],
    OrderStatus.CLIENT_CONFIRMED: ["on_way_to_pickup"],
}

LOCATION_PROMPT_STATUSES = {
    OrderStatus.ON_THE_WAY_TO_PICKUP,
    OrderStatus.ON_THE_WAY_WITH_CARGO,
    OrderStatus.AT_DROPOFF_LOCATION,
}

@router.callback_query(F.data == "driver_orders")
async def show_driver_orders(call: CallbackQuery):
    driver = await BotService.get_driver_by_telegram_id(call.from_user.id)
    if not driver:
        await call.answer("Haydovchi topilmadi!", show_alert=True)
        return

    orders = await BotService.get_driver_orders(driver)
    if not orders:
        await safe_edit_text(call.message, "Sizda faol buyurtmalar yo'q.", reply_markup=get_driver_main_keyboard())
    else:
        await safe_edit_text(call.message, "Buyurtmangizni tanlang:", reply_markup=get_order_list_keyboard(orders, "driver"))

@router.callback_query(F.data.startswith("order_detail_driver_"))
async def show_order_detail(call: CallbackQuery):
    order_id_part = call.data.split("_")[-1]
    if not order_id_part.isdigit():
        await call.answer("Xato ma'lumot, ro'yxatdan qayta tanlang", show_alert=True)
        await safe_edit_text(call.message, "Bosh menyu:", reply_markup=get_driver_main_keyboard())
        return
    order_id = int(order_id_part)
    driver = await BotService.get_driver_by_telegram_id(call.from_user.id)
    if not driver:
        await call.answer("Haydovchi topilmadi!", show_alert=True)
        return

    order = await BotService.get_order_for_driver(order_id, driver)

    if not order:
        await call.answer("Buyurtma topilmadi!", show_alert=True)
        return

    pickup = await BotService.get_pickup_point(order)
    dropoff = await BotService.get_dropoff_point(order)
    pickup_addr = pickup.address if pickup else "Noma'lum"
    dropoff_addr = dropoff.address if dropoff else "Noma'lum"

    text = f"📦 Buyurtma #{order.public_id[-6:]}\n\n" \
           f"📍 Olish: {pickup_addr}\n" \
           f"🏁 Tushirish: {dropoff_addr}\n" \
           f"💰 Narx: {order.driver_price:,.0f} so'm\n" \
           f"📅 Vaqt: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n" \
           f"🔄 Status: {order.get_current_status_display()}\n"

    await safe_edit_text(call.message, text, reply_markup=get_driver_order_actions_keyboard(order.id, order.current_status))

@router.callback_query(F.data.startswith("status_menu_"))
async def show_status_menu(call: CallbackQuery):
    match = STATUS_MENU_RE.match(call.data)
    if not match:
        await call.answer("Xato ma'lumot", show_alert=True)
        return
    order_id = int(match.group(1))
    driver = await BotService.get_driver_by_telegram_id(call.from_user.id)
    if not driver:
        await call.answer("Haydovchi topilmadi!", show_alert=True)
        return

    order = await BotService.get_order_for_driver(order_id, driver)
    if not order:
        await call.answer("Buyurtma topilmadi!", show_alert=True)
        return

    await safe_edit_text(call.message, "Yangi statusni tanlang:", reply_markup=get_driver_status_change_keyboard(order.id, order.current_status))

@router.callback_query(F.data.startswith("status_pick_"))
async def pick_status(call: CallbackQuery, state: FSMContext):
    match = STATUS_PICK_RE.match(call.data)
    if not match:
        await call.answer("Xato ma'lumot", show_alert=True)
        return

    order_id = int(match.group(1))
    status_code = match.group(2)

    driver = await BotService.get_driver_by_telegram_id(call.from_user.id)
    order = await BotService.get_order_for_driver(order_id, driver) if driver else None
    if not order:
        await call.answer("Buyurtma topilmadi!", show_alert=True)
        return

    if status_code not in ALLOWED_STATUS_BY_CURRENT.get(order.current_status, []):
        await call.answer("Bu statusga o'tish mumkin emas", show_alert=True)
        return

    target_status, requires_video = STATUS_OPTION_MAP.get(status_code, (None, False))
    if not target_status:
        await call.answer("Status topilmadi", show_alert=True)
        return

    if requires_video:
        await state.update_data(order_id=order_id, target_status=target_status.name)
        await state.set_state(DriverOrderState.waiting_for_proof)
        await call.message.answer("📹 Iltimos, statusni tasdiqlash uchun VIDEO yuboring (📎 -> Video).", reply_markup=get_back_keyboard())
        await call.answer()
        return

    updated_order = await BotService.update_order_status(order_id, target_status, driver=driver)
    if updated_order:
        await call.answer("✅ Status yangilandi!")

        # Refresh order from DB
        refreshed_order = await BotService.get_order_for_driver(order_id, driver)
        pickup = await BotService.get_pickup_point(refreshed_order)
        dropoff = await BotService.get_dropoff_point(refreshed_order)
        pickup_addr = pickup.address if pickup else "Noma'lum"
        dropoff_addr = dropoff.address if dropoff else "Noma'lum"

        text = f"📦 Buyurtma #{refreshed_order.public_id[-6:]}\n\n" \
               f"📍 Olish: {pickup_addr}\n" \
               f"🏁 Tushirish: {dropoff_addr}\n" \
               f"💰 Narx: {refreshed_order.driver_price:,.0f} so'm\n" \
               f"📅 Vaqt: {refreshed_order.created_at.strftime('%Y-%m-%d %H:%M')}\n" \
               f"🔄 Status: {refreshed_order.get_current_status_display()}\n"

        await safe_edit_text(call.message, text, reply_markup=get_driver_order_actions_keyboard(refreshed_order.id, refreshed_order.current_status))
    else:
        await call.answer("❌ Statusni yangilab bo'lmadi", show_alert=True)

@router.callback_query(F.data.startswith("proof_request_"))
async def request_proof(call: CallbackQuery, state: FSMContext):
    # Format: proof_request_{order_id}_{target_status}
    parts = call.data.split("_")
    order_id = int(parts[2])
    target_status_code = parts[3]

    # Map target strings to Enum
    status_map = {
        "loaded": OrderStatus.LOADED,
        "unloading_requested": OrderStatus.UNLOADING_REQUESTED,
        "unloading_confirmed": OrderStatus.UNLOADING_CONFIRMED,
    }
    target_status = status_map.get(target_status_code)

    if not target_status:
         await call.answer("Noto'g'ri status!", show_alert=True)
         return

    await state.update_data(order_id=order_id, target_status=target_status.name)
    await state.set_state(DriverOrderState.waiting_for_proof)

    await call.message.answer("📹 Iltimos, statusni tasdiqlash uchun VIDEO yuboring (📎 -> Video).", reply_markup=get_back_keyboard())
    await call.answer()

@router.message(DriverOrderState.waiting_for_proof, F.photo | F.video | F.document)
async def process_proof(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")
    target_status_name = data.get("target_status")

    driver = await BotService.get_driver_by_telegram_id(message.from_user.id)
    order = await BotService.get_order_for_driver(order_id, driver) if driver else None
    if not order:
        await message.answer("Buyurtma topilmadi yoki sizga tegishli emas.")
        await state.clear()
        return

    if not target_status_name:
        await message.answer("Status aniqlanmadi, qayta urinib ko'ring.")
        await state.clear()
        return

    target_status = OrderStatus[target_status_name]

    if not message.video:
        await message.answer("Faqat video yuboring (📎 -> Video).")
        return

    file_id = message.video.file_id
    proof_kind = ProofKind.VIDEO
    file_name = f"proof_{order_id}_{target_status.name.lower()}.mp4"

    file_info = await message.bot.get_file(file_id)
    file_io = io.BytesIO()
    await message.bot.download_file(file_info.file_path, destination=file_io)
    django_file = ContentFile(file_io.getvalue(), name=file_name)

    updated_order = await BotService.update_order_status(
        order_id,
        target_status,
        driver=driver,
        proof_file=django_file,
        proof_type=proof_kind
    )

    if updated_order:
        await message.answer("✅ Video qabul qilindi. Status yangilandi.", reply_markup=get_driver_main_keyboard())
    else:
        await message.answer("Statusni yangilashda xatolik yuz berdi.")

    await state.clear()

@router.callback_query(F.data.startswith("send_loc_"))
async def send_location_prompt(call: CallbackQuery, state: FSMContext):
    try:
        order_id = int(call.data.split("_")[-1])
    except (ValueError, IndexError):
        await call.answer("Xato ma'lumot", show_alert=True)
        return
    await state.update_data(location_order_id=order_id)

    # Send friendly message to driver requesting location
    await call.message.answer(
        f"📍 **Lokatsiyani yuboring**\n\n"
        f"Buyurtma #{order_id} uchun hozirgi lokatsiyanginni yuboring.\n"
        f"(📎 tugmasini bosing → Location)",
        reply_markup=get_back_keyboard()
    )
    await call.answer()

@router.message(F.location)
async def process_location(message: Message, state: FSMContext):
    driver = await BotService.get_driver_by_telegram_id(message.from_user.id)
    if driver:
        # Get order_id from state if available (from send_loc callback)
        data = await state.get_data()
        order_id = data.get("location_order_id")

        if order_id:
            try:
                order_id = int(order_id)
                # Update driver location in DB
                await BotService.update_driver_location(
                    driver.id,
                    message.location.latitude,
                    message.location.longitude,
                    order_id=order_id
                )

                # Send confirmation to driver
                await message.answer(
                    "✅ **Lokatsiya yuborildi!**\n\n"
                    "Mijoz hozirgi lokatsiyanginni ko'rishi mumkin.",
                    reply_markup=get_driver_main_keyboard()
                )

                # Notify customer that location has been shared
                order = await BotService.get_order_by_id(order_id)
                if order and order.client.telegram_id:
                    loc_text = f"📍 **Haydovchining lokatsiyasi**\n\n" \
                               f"Latitude: {message.location.latitude}\n" \
                               f"Longitude: {message.location.longitude}\n\n" \
                               f"📦 Buyurtma: #{order.public_id[-6:]}"
                    try:
                        await BotService.send_message(
                            order.client.telegram_id,
                            loc_text
                        )
                    except:
                        pass

                await state.clear()
            except (ValueError, TypeError) as e:
                await message.answer(
                    f"❌ Xatolik yuz berdi: {str(e)}\n\nQayta urinib ko'ring.",
                    reply_markup=get_driver_main_keyboard()
                )
                await state.clear()
        else:
            # No specific order, just update location
            await BotService.update_driver_location(
                driver.id,
                message.location.latitude,
                message.location.longitude,
            )
            await message.answer(
                "✅ Lokatsiya yangilandi.",
                reply_markup=get_driver_main_keyboard()
            )
            await state.clear()
    else:
        await message.answer("❌ Haydovchi topilmadi!")
        await state.clear()

@router.callback_query(F.data == "back_home")
async def back_home(call: CallbackQuery, state: FSMContext):
    await state.clear()
    driver = await BotService.get_driver_by_telegram_id(call.from_user.id)
    kb = get_driver_main_keyboard() if driver else get_customer_main_keyboard()
    await safe_edit_text(call.message, "Bosh menyu:", reply_markup=kb)
