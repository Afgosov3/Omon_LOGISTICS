from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    waiting_for_phone = State()

class DriverOrderState(StatesGroup):
    waiting_for_proof = State()
    viewing_order = State()

class CustomerOrderState(StatesGroup):
    viewing_order = State()

