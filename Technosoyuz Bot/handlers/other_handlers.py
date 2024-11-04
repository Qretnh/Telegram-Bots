from aiogram import Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, Contact
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter
from keyboards.price_keyboards import generate_price_keyboard, send_number_keyboard
from services.business_logic import get_name_from_callback
from aiogram.types import callback_query
from db.user_contacts import users_contacts

router = Router()


@router.message()
async def other_messages(message: Message):
    await message.answer(text=f'Я не понял ваше сообщение. для запроса прайс-листа введите /price',
                         reply_markup=None)
