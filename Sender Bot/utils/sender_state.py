from aiogram.fsm.state import State, StatesGroup


class Steps(StatesGroup):
    get_message = State()
    q_button = State()
    get_text_button = State()
    get_link_button = State()
    confirm = State()
