from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    waiting_for_phone = State()

class DriverOrderState(StatesGroup):
    waiting_for_proof = State()
    viewing_order = State()

class CustomerOrderState(StatesGroup):
    viewing_order = State()

class SettingsState(StatesGroup):
    edit_first_name = State()
    edit_last_name = State()
