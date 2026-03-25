from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services import BotService
from telegram_bot.keyboards.keyboards import get_phone_keyboard, get_driver_main_keyboard, get_customer_main_keyboard
from telegram_bot.states.states import RegistrationState

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id

    # Check if user exists
    driver = await BotService.get_driver_by_telegram_id(telegram_id)
    if driver:
        await message.answer(f"Xush kelibsiz, haydovchi {driver.full_name}!", reply_markup=get_driver_main_keyboard())
        return

    customer = await BotService.get_customer_by_telegram_id(telegram_id)
    if customer:
        client = customer # BotService returns Client
        await message.answer(f"Xush kelibsiz, mijoz {client.full_name}!", reply_markup=get_customer_main_keyboard())
        return

    await message.answer(
        "Assalomu alaykum! Tizimga kirish uchun telefon raqamingizni yuboring.",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(RegistrationState.waiting_for_phone)

@router.message(RegistrationState.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    contact = message.contact
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()

    role, user = await BotService.register_user(message.from_user.id, contact.phone_number, full_name)

    if role == "driver":
        await message.answer(f"Tabriklaymiz! Siz haydovchi sifatida tizimga kirdingiz: {user.full_name}", reply_markup=get_driver_main_keyboard())
        await state.clear()
    elif role == "customer":
        await message.answer(f"Tabriklaymiz! Siz mijoz sifatida tizimga kirdingiz: {user.full_name}", reply_markup=get_customer_main_keyboard())
        await state.clear()
    else:
        await message.answer(
            "Kechirasiz, siz tizimda topilmadingiz. Iltimos, dispetcher bilan bog'laning.",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()

