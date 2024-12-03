from config_data.config import config
from aiogram.filters.command import Command
from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.types import Message, CallbackQuery
from keyboards.admin_keyboards import admin_keyboard
from database.database import DB
import asyncio

router = Router()


class FSMSender(StatesGroup):
    text = State()


@router.message(Command(commands=['admin']))
async def admin_panel(message: Message):
    await message.answer(text="Админ-Панель",
                         reply_markup=admin_keyboard)


@router.callback_query(F.data == 'sender')
async def config_sender(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text="Введите сообщение для рассылки")
    await state.set_state(FSMSender.text)


@router.message(StateFilter(FSMSender.text))
async def start_send(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(default_state)
    await message.answer(text="Рассылка началась...")
    ctr = 0
    users = await DB.get_all_users()
    for user in users:
        try:
            await bot.copy_message(chat_id=user, from_chat_id=message.from_user.id, message_id=message.message_id)
            ctr += 1
        except Exception as e:
            print(f"Ошибка при отправке сообщения id{user}: {e}")
        finally:
            await asyncio.sleep(0.05)

    await message.answer(text=f"Рассылка завершена. успешно отправлено {ctr} сообщений")

