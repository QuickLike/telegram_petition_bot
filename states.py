from aiogram.fsm.state import State, StatesGroup


class Petition(StatesGroup):
    first_name = State()
    last_name = State()
    username = State()
    message_id = State()
    text = State()
