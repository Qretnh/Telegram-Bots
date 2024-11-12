from aiogram.fsm.state import State, StatesGroup


class FSMSupport(StatesGroup):
    send_appeal = State()
    admin = State()
    admin_appeal_answer = State()
    admin_enter_ban = State()
    admin_enter_unban = State()