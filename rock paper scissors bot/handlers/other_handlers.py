from aiogram import Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU
from keyboards.keyboards import offer_keyboard, choose_keyboard, wait_keyboard
from services.game_logic import move

router = Router()


@router.message()
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['dunno'],
                         reply_markup=offer_keyboard)
