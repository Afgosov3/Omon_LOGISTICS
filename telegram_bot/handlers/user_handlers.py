from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from telegram_bot.services import BotService
from telegram_bot.keyboards.keyboards import get_phone_keyboard, get_driver_main_keyboard, get_customer_main_keyboard, get_settings_keyboard
from telegram_bot.states.states import RegistrationState, SettingsState
import re

router = Router()

NAME_PATTERN = re.compile(r"^[A-Za-z\u0400-\u04FF' -]{2,50}$")

async def safe_edit_text(message, text, reply_markup=None):
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        raise

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id

    # Check if user exists
    driver = await BotService.get_driver_by_telegram_id(telegram_id)
    if driver:
        kb = get_driver_main_keyboard()
        await message.answer(
            f"🚗 **Xush kelibsiz, haydovchi {driver.full_name}!**\n\n"
            f"📊 Aktiv buyurtmalar va statuslarni kuzatib boring.",
            reply_markup=kb
        )
        await state.clear()
        return

    customer = await BotService.get_customer_by_telegram_id(telegram_id)
    if customer:
        kb = get_customer_main_keyboard()
        await message.answer(
            f"👤 **Xush kelibsiz, {customer.full_name}!**\n\n"
            f"📦 O'zingizning buyurtmalaringizni kuzatib boring.",
            reply_markup=kb
        )
        await state.clear()
        return

    # New user registration
    await message.answer(
        "👋 **Assalomu alaykum!**\n\n"
        "🚗 **OMON Logistics** - sifat va ishonchni talab qiladigan yuk tashish xizmati.\n\n"
        "📱 Telefon raqamingizni yuboring, tizimga kirish uchun.",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(RegistrationState.waiting_for_phone)

@router.message(RegistrationState.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    contact = message.contact
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()

    role, user = await BotService.register_user(message.from_user.id, contact.phone_number, full_name)

    if role == "driver":
        text = (
            f"✅ **Haydovchi sifatida ro'yxatdan o'tdingiz!**\n\n"
            f"🚗 **Ism:** {user.full_name}\n"
            f"📞 **Telefon:** {contact.phone_number}\n\n"
            f"Buyurtmalarni ko'rish uchun 📦 **Buyurtmalarim** tugmasini bosing."
        )
        await message.answer(text, reply_markup=get_driver_main_keyboard())
        await state.clear()
    elif role == "customer":
        text = (
            f"✅ **Mijoz sifatida ro'yxatdan o'tdingiz!**\n\n"
            f"👤 **Ism:** {user.full_name}\n"
            f"📞 **Telefon:** {contact.phone_number}\n\n"
            f"Buyurtmalarni ko'rish uchun 📦 **Buyurtmalarim** tugmasini bosing."
        )
        await message.answer(text, reply_markup=get_customer_main_keyboard())
        await state.clear()
    else:
        text = (
            "❌ **Ro'yxatdan o'tishda xatolik!**\n\n"
            "Sizning telefon raqamingiz tizimda topilmadi.\n"
            "Iltimos, dispetcher bilan bog'laning yoki qayta urinib ko'ring."
        )
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
        await state.clear()

@router.callback_query(F.data == "settings_menu")
async def open_settings(call: CallbackQuery, state: FSMContext):
    await state.clear()
    driver = await BotService.get_driver_by_telegram_id(call.from_user.id)
    customer = await BotService.get_customer_by_telegram_id(call.from_user.id)

    if not driver and not customer:
        await call.answer("Avval ro'yxatdan o'ting", show_alert=True)
        await safe_edit_text(call.message, "Telefon raqamingizni yuboring:", reply_markup=get_phone_keyboard())
        return

    role = "driver" if driver else "customer"
    await state.update_data(role=role, driver_id=getattr(driver, "id", None), customer_id=getattr(customer, "id", None))
    await safe_edit_text(call.message, "⚙️ Sozlamalar menyusi", reply_markup=get_settings_keyboard())

@router.callback_query(F.data == "edit_first_name")
async def start_first_name_edit(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("role"):
        await open_settings(call, state)
        return
    await state.set_state(SettingsState.edit_first_name)
    await call.message.answer("✏️ Yangi ismingizni kiriting (2-50 ta belgi):", reply_markup=ReplyKeyboardRemove())
    await call.answer()

@router.callback_query(F.data == "edit_last_name")
async def start_last_name_edit(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("role"):
        await open_settings(call, state)
        return
    await state.set_state(SettingsState.edit_last_name)
    await call.message.answer("✏️ Yangi familiyangizni kiriting (2-50 ta belgi):", reply_markup=ReplyKeyboardRemove())
    await call.answer()

@router.message(SettingsState.edit_first_name, F.text)
async def process_first_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not NAME_PATTERN.match(name):
        await message.answer("Ism faqat harflar va '-' belgisidan iborat bo'lishi va 2-50 belgi oralig'ida bo'lishi kerak.")
        return

    data = await state.get_data()
    role = data.get("role")
    if role == "driver" and data.get("driver_id"):
        user = await BotService.update_driver_name(data["driver_id"], first_name=name)
    elif role == "customer" and data.get("customer_id"):
        user = await BotService.update_client_name(data["customer_id"], first_name=name)
    else:
        user = None

    await state.clear()

    if user:
        kb = get_driver_main_keyboard() if role == "driver" else get_customer_main_keyboard()
        await message.answer(f"✅ Ism yangilandi: {user.full_name}", reply_markup=kb)
    else:
        await message.answer("❌ Yangilashda xatolik. Qayta urinib ko'ring.")

@router.message(SettingsState.edit_last_name, F.text)
async def process_last_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not NAME_PATTERN.match(name):
        await message.answer("Familiya faqat harflar va '-' belgisidan iborat bo'lishi va 2-50 belgi oralig'ida bo'lishi kerak.")
        return

    data = await state.get_data()
    role = data.get("role")
    if role == "driver" and data.get("driver_id"):
        user = await BotService.update_driver_name(data["driver_id"], last_name=name)
    elif role == "customer" and data.get("customer_id"):
        user = await BotService.update_client_name(data["customer_id"], last_name=name)
    else:
        user = None

    await state.clear()

    if user:
        kb = get_driver_main_keyboard() if role == "driver" else get_customer_main_keyboard()
        await message.answer(f"✅ Familiya yangilandi: {user.full_name}", reply_markup=kb)
    else:
        await message.answer("❌ Yangilashda xatolik. Qayta urinib ko'ring.")

@router.message(SettingsState.edit_first_name)
@router.message(SettingsState.edit_last_name)
async def reject_non_text(message: Message):
    await message.answer("Iltimos, faqat matn kiriting.")
