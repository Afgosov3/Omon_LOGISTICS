from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services import BotService
from telegram_bot.keyboards.keyboards import (
    get_driver_main_keyboard,
    get_order_list_keyboard,
    get_driver_order_actions_keyboard,
    get_back_keyboard, get_customer_main_keyboard
)
from telegram_bot.states.states import DriverOrderState
from orders.models import OrderStatus, ProofKind
from django.core.files.base import ContentFile
from django.conf import settings
import io

router = Router()

@router.callback_query(F.data == "driver_orders")
async def show_driver_orders(call: CallbackQuery):
    driver = await BotService.get_driver_by_telegram_id(call.from_user.id)
    if not driver:
        await call.answer("Haydovchi topilmadi!", show_alert=True)
        return

    orders = await BotService.get_driver_orders(driver)
    if not orders:
        await call.message.edit_text("Sizda faol buyurtmalar yo'q.", reply_markup=get_driver_main_keyboard())
    else:
        await call.message.edit_text("Buyurtmangizni tanlang:", reply_markup=get_order_list_keyboard(orders, "driver"))

@router.callback_query(F.data.startswith("order_detail_driver_"))
async def show_order_detail(call: CallbackQuery):
    order_id = int(call.data.split("_")[-1])
    order = await BotService.get_order_by_id(order_id)

    if not order:
        await call.answer("Buyurtma topilmadi!", show_alert=True)
        return

    pickup = await BotService.get_pickup_point(order)
    dropoff = await BotService.get_dropoff_point(order)
    pickup_addr = pickup.address if pickup else "Noma'lum"
    dropoff_addr = dropoff.address if dropoff else "Noma'lum"

    client_name = order.client.full_name if order.client else "Noma'lum"
    client_phone = order.client.phone if order.client else ""

    text = f"📦 Buyurtma #{order.public_id[-6:]}\n\n" \
           f"📍 Olish: {pickup_addr}\n" \
           f"🏁 Tushirish: {dropoff_addr}\n" \
           f"💰 Narx: {order.driver_price:,.0f} so'm\n" \
           f"👤 Mijoz: {client_name}\n" \
           f"📞 Tel: {client_phone}\n" \
           f"📅 Vaqt: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n" \
           f"🔄 Status: {order.get_current_status_display()}\n"

    # Determine status flow logic here or in keyboard generator
    await call.message.edit_text(text, reply_markup=get_driver_order_actions_keyboard(order.id, order.current_status))

@router.callback_query(F.data.startswith("status_"))
async def update_status_direct(call: CallbackQuery):
    # Format: status_{order_id}_{new_status_code}
    parts = call.data.split("_")
    order_id = int(parts[1])

    # Map button codes to model statuses
    status_map = {
        "on_way_to_pickup": OrderStatus.ON_THE_WAY_TO_PICKUP,
        "at_pickup_location": OrderStatus.AT_PICKUP_LOCATION,
        "on_the_way_with_cargo": OrderStatus.ON_THE_WAY_WITH_CARGO,
        "at_dropoff_location": OrderStatus.AT_DROPOFF_LOCATION,
    }

    action = "_".join(parts[2:])
    new_status = status_map.get(action)

    if new_status:
        driver = await BotService.get_driver_by_telegram_id(call.from_user.id)
        order = await BotService.update_order_status(order_id, new_status, driver=driver)
        if order:
            await call.answer(f"Status yangilandi: {new_status}")
            # Refresh view
            await show_order_detail(call)
        else:
             await call.answer("Xatolik yuz berdi", show_alert=True)
    else:
        await call.answer("Status xatosi", show_alert=True)

@router.callback_query(F.data.startswith("proof_request_"))
async def request_proof(call: CallbackQuery, state: FSMContext):
    # Format: proof_request_{order_id}_{target_status}
    parts = call.data.split("_")
    order_id = int(parts[2])
    target_status_code = parts[3]

    # Map target strings to Enum
    status_map = {
        "loaded": OrderStatus.LOADED,
        "unloading_confirmed": OrderStatus.UNLOADING_CONFIRMED,
        "completed": OrderStatus.COMPLETED
    }
    target_status = status_map.get(target_status_code)

    if not target_status:
         await call.answer("Noto'g'ri status!", show_alert=True)
         return

    await state.update_data(order_id=order_id, target_status=target_status)
    await state.set_state(DriverOrderState.waiting_for_proof)

    await call.message.answer("📸 Iltimos, rasm yoki video yuklang (isbot sifatida):", reply_markup=get_back_keyboard())
    await call.answer()

@router.message(DriverOrderState.waiting_for_proof, F.photo | F.video | F.document)
async def process_proof(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")
    target_status = data.get("target_status")

    driver = await BotService.get_driver_by_telegram_id(message.from_user.id)

    file_id = None
    proof_kind = None
    file_name = f"proof_{order_id}_{target_status}"

    if message.photo:
        file_id = message.photo[-1].file_id # Best quality
        proof_kind = ProofKind.IMAGE
        file_name += ".jpg"
    elif message.video:
        file_id = message.video.file_id
        proof_kind = ProofKind.VIDEO
        file_name += ".mp4"
    elif message.document:
        file_id = message.document.file_id
        proof_kind = ProofKind.DOCUMENT
        file_name += f"_{message.document.file_name}"

    if file_id:
        file_info = await message.bot.get_file(file_id)
        # Download file
        file_io = io.BytesIO()
        await message.bot.download_file(file_info.file_path, destination=file_io)

        django_file = ContentFile(file_io.getvalue(), name=file_name)

        await BotService.update_order_status(
            order_id,
            target_status,
            driver=driver,
            proof_file=django_file,
            proof_type=proof_kind
        )

        await message.answer(f"✅ Isbot qabul qilindi. Buyurtma statusi yangilandi.", reply_markup=get_driver_main_keyboard())
    else:
        await message.answer("Fayl yuklashda xatolik!")

    await state.clear()

@router.callback_query(F.data == "driver_location")
async def ask_location(call: CallbackQuery):
    await call.message.answer("📍 Iltimos, lokatsiyanginni yuboring (📎 -> Location).", reply_markup=get_back_keyboard())
    await call.answer()

@router.message(F.location)
async def process_location(message: Message):
    driver = await BotService.get_driver_by_telegram_id(message.from_user.id)
    if driver:
        await BotService.update_driver_location(driver.id, message.location.latitude, message.location.longitude)
        await message.answer("✅ Lokatsiya yangilandi!", reply_markup=get_driver_main_keyboard())
    else:
        # Check if customer in future? Or ignore.
        pass

@router.callback_query(F.data == "back_home")
async def back_home(call: CallbackQuery, state: FSMContext):
    await state.clear()
    driver = await BotService.get_driver_by_telegram_id(call.from_user.id)
    if driver:
        await call.message.edit_text("Bosh menyu:", reply_markup=get_driver_main_keyboard())
    else:
        await call.message.edit_text("Bosh menyu:", reply_markup=get_customer_main_keyboard())

