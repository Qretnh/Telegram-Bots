from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class cryptobot(StatesGroup):
    amount = State()
    payment = State()


class cryptomus(StatesGroup):
    amount = State()
    payment = State()


class yoomoney(StatesGroup):
    amount = State()
    payment = State()
