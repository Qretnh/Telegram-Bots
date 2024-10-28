from aiogram import Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU
from keyboards.keyboards import offer_keyboard, choose_keyboard, wait_keyboard
from services.game_logic import move, stats, update_stats

router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=offer_keyboard)


# Этот хэндлер срабатывает на команду /help

@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'],
                         reply_markup=offer_keyboard)


@router.message(Command(commands='stats'))
async def process_help_command(message: Message):
    await message.answer(text=stats(message.from_user.id),
                         reply_markup=offer_keyboard)


@router.message((lambda message: 'Давай' in message.text))
async def start_game(message: Message):
    await message.answer(text=LEXICON_RU['game'],
                         reply_markup=choose_keyboard)


@router.message(F.text == 'Камень🪨')
@router.message(F.text == 'Ножницы✂️')
@router.message(F.text == 'Бумага📄')
async def game(message: Message):
    result, answer = move(message.text)
    update_stats(id=message.from_user.id, win=(0 if result == 'lose' else 1))

    await message.answer(text=f"Мой ответ... \n\n{answer}")
    await message.answer(text=LEXICON_RU[result],
                         reply_markup=offer_keyboard)
    await message.answer(text=f"Сыграем ещё?")


@router.message(F.text == 'Не хочу')
async def wait(message: Message):
    await message.answer(text=LEXICON_RU['wait'], reply_markup=wait_keyboard)
