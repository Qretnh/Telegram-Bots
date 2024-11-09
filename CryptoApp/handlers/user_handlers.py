from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.keyboards import choose_language_keyboard, get_countries_keyboard, russia_banks_keyboard, \
    generate_captcha_keyboard, gen_menu_keyboard
# from services.business_logic import get_name_from_callback
from aiogram.types import callback_query
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, Redis
from lexicon.lexicon import lexicon as lexicon
import asyncio
from services.menu import menu_buttons
from random import randint


class FSMAuth(StatesGroup):
    choose_language = State()
    enter_captcha = State()
    hello_message = State()
    complete_launching = State()
    banned = State()
    admin_set = State()


storage = MemoryStorage()
router = Router()


@router.message(Command(commands=['start']))
async def start(message: Message, state: FSMContext):
    await message.answer(text="Please, choose your language:",
                         reply_markup=choose_language_keyboard)
    await state.set_state(FSMAuth.choose_language)


@router.callback_query(StateFilter(FSMAuth.choose_language))
async def set_EN(callback: CallbackQuery, state: FSMContext):
    await state.update_data(language=callback.data)
    state_info = await state.get_data()
    language = state_info['language']

    await state.set_state(FSMAuth.enter_captcha)
    await callback.message.answer(text=lexicon["captcha"][language])
    gen_captcha_text, gen_captcha_keyboard = generate_captcha_keyboard()
    await callback.message.answer(text=gen_captcha_text,
                                  reply_markup=gen_captcha_keyboard)


@router.callback_query(StateFilter(FSMAuth.enter_captcha), F.data == 'Stop')
async def wrong_captcha(callback: CallbackQuery, state: FSMContext, language: str):
    await callback.message.answer(text=lexicon['try'][language])
    gen_captcha_text, gen_captcha_keyboard = generate_captcha_keyboard(second_try=True)
    await callback.message.answer(text=gen_captcha_text,
                                  reply_markup=gen_captcha_keyboard())


@router.callback_query(StateFilter(FSMAuth.enter_captcha), F.data == 'Pass')
async def greeting_message(callback: CallbackQuery, state: FSMContext, language: str):
    await callback.message.answer(text=lexicon['pass'][language])
    await state.set_state(FSMAuth.complete_launching)
    await callback.message.answer(text=lexicon['menu'][language],
                                  reply_markup=gen_menu_keyboard())


@router.callback_query(StateFilter(FSMAuth.enter_captcha), F.data == 'Ban')
async def greeting_message_ban(callback: CallbackQuery, state: FSMContext, language: str):
    await callback.message.answer(text=lexicon['ban'][language])
    await state.set_state(FSMAuth.banned)
    await asyncio.sleep(3600)
    await state.set_state(FSMAuth.enter_captcha)
    await callback.message.answer(text=lexicon["captcha"][language])


@router.message(Command(commands=['menu']), StateFilter(FSMAuth.complete_launching))
async def banking_apps(message: Message, state: FSMContext, language: str):
    await message.answer(text=lexicon['menu'][language],
                         reply_markup=gen_menu_keyboard)


@router.callback_query(F.data == 'banks', StateFilter(FSMAuth.complete_launching))
async def banking_apps(callback: CallbackQuery, state: FSMContext, language):
    keyboard = get_countries_keyboard(language)
    await callback.message.answer(text=lexicon['choose_country'][language],
                                  reply_markup=keyboard)


@router.callback_query(F.data == 'Россия', StateFilter(FSMAuth.complete_launching))
async def russia_banks(callback: CallbackQuery, state: FSMContext, language):
    await callback.message.answer(text='Выберите банк',
                                  reply_markup=russia_banks_keyboard)
