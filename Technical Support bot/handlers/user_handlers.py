from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Router, F
from aiogram.filters import CommandObject, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from config_data.config import config
from utils.dbconnect import Request
from keyboards.admin_keyboards import admin_menu_keyboard
from utils.FSM import FSMSupport

admin_chat_id = config.tg_bot.admin_ids[0]
router = Router()


@router.message(Command(commands=['start']))
async def start(message: Message):
    await message.answer('Здравствуйте, это бот технической поддержки \n\n'
                         '/support - Обратиться в поддержку\n'
                         '/faq - Ответы на самые частые вопросы\n')


@router.callback_query(F.data == 'start')
async def start_cb(callback: CallbackQuery):
    await callback.message.answer('Здравствуйте, это бот технической поддержки \n\n'
                                  '/support - Написать обращение в поддержку\n')
    await callback.answer()


@router.message(Command(commands=['support']))
async def start(message: Message, state: FSMContext):
    await message.answer('Среднее время ожидания ответа ~<b>1 час</b>\n\n'
                         'Если передумали, можете нажать на кнопку ниже\n'
                         'Напишите ваше обращение:',
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=
                         [
                             [
                                 InlineKeyboardButton(text='Отменить обращение',
                                                      callback_data='start')
                             ]
                         ]))
    await state.set_state(FSMSupport.send_appeal)


@router.message(StateFilter(FSMSupport.send_appeal))
async def send_appeal(message: Message, bot: Bot, state: FSMContext, request: Request):
    await state.set_state(default_state)
    await message.answer(text='Спасибо!\nВаше обращение успешно отправлено. Ответ придёт вам в этот чат.')
    await bot.send_message(admin_chat_id, f'Новое обращение от пользователя: {message.from_user.id}\n\n{message.from_user.first_name}\n"{message.text}"')
    await request.add_data(message.from_user.id, message.text, str(message.from_user.id)+'_'+str(message.message_id))
