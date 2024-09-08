from aiogram.fsm.state import StatesGroup, State

class AddMessageState(StatesGroup):
    waiting_for_message = State()
