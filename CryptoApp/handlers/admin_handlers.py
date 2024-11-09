from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter
from keyboards.keyboards import admin_menu_keyboard, gen_menu_keyboard
from services.admins import admins_id
from handlers.user_handlers import FSMAuth
from services.menu import menu_buttons, check_cb

router = Router()


@router.message(Command(commands=['admin']), lambda message: message.from_user.id in admins_id)
async def admin_menu(message: Message, state: FSMContext):
    await message.answer(text='Админ-панель',
                         reply_markup=admin_menu_keyboard)


@router.callback_query(F.data == 'change_message', lambda message: message.from_user.id in admins_id)
async def admin_menu_choose(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Выберите кнопку для редактирования',
                                  reply_markup=gen_menu_keyboard(admin=True))


@router.callback_query(F.data.startswith('set_text'), lambda message: message.from_user.id in admins_id)
async def admin_menu_set_button(callback: CallbackQuery, state: FSMContext):
    button = callback.data.split()[1]
    await callback.message.answer(text='Введите новый текст для кнопки')
    await state.update_data({'update_button': button})
    await state.set_state(FSMAuth.admin_set)


@router.message(StateFilter(FSMAuth.admin_set))
async def admin_enter_text(message: Message, state: FSMContext):
    cb = await state.get_data()
    number = check_cb(cb['update_button'])
    menu_buttons[number] = message.text
    await message.answer(text='Кнопка обновлена!')
    await state.set_state(FSMAuth.complete_launching)
