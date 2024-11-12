from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Router, F
from aiogram.filters import CommandObject, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from config_data.config import config
from keyboards.admin_keyboards import admin_menu_keyboard, admin_ban_unban_keyboard
from utils.dbconnect import Request
from utils.FSM import FSMSupport

router = Router()
admin_chat_id = config.tg_bot.admin_ids[0]


@router.message(Command(commands=['admin']))
async def admin_menu(message: Message, state: FSMContext):
    if message.from_user.id != admin_chat_id:
        await message.answer("Вы не имеете доступа к этой команде")
    else:
        await state.set_state(FSMSupport.admin)
        await message.answer(text="Панель управления",
                             reply_markup=admin_menu_keyboard)


@router.callback_query(F.data == 'new_appeals')
async def new_appeals(callback: CallbackQuery, state: FSMContext, request: Request):
    count = await request.fetch_appeals_count()

    keyboard = None
    if count > 0:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Просмотреть',
                                                                               callback_data='check_appeals')]])

    await callback.message.edit_text(text=f"Новых обращений: {count}")

    if count > 0:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == 'check_appeals')
async def check_appeals(callback: CallbackQuery, state: FSMContext, request: Request):
    appeals = await request.fetch_appeals()
    for appeal in appeals:
        await callback.message.answer(
            text=f'Обращение от пользователя: {appeal[3]}\n\n"{appeal[2]}"',
            reply_markup=
            InlineKeyboardMarkup(inline_keyboard=
                                 [[InlineKeyboardButton(text="Ответить",
                                                        callback_data=f"answer_{appeal[0]}")]]))
    await callback.answer()


@router.callback_query(F.data.startswith('answer'))
async def answer(callback: CallbackQuery, bot: Bot, state: FSMContext, request: Request):
    user_id, user_message_id = int(callback.data.split('_')[1]), int(callback.data.split('_')[2])
    await bot.copy_message(admin_chat_id, user_id, user_message_id)
    await callback.message.answer(text=f"Введите текст для ответа на сообщение:")
    await state.update_data({'id_to_answer': callback.data[7:]})
    await state.set_state(FSMSupport.admin_appeal_answer)
    await callback.answer()


@router.message(StateFilter(FSMSupport.admin_appeal_answer))
async def admin_appeal_answer(message: Message, bot: Bot, state: FSMContext, request: Request):
    data = await state.get_data()
    chat_id = int(data['id_to_answer'].split('_')[0])
    unique_appeal_id = data['id_to_answer']
    await bot.send_message(chat_id, text='На ваше обращение пришёл ответ')
    await bot.copy_message(chat_id, admin_chat_id, message.message_id)
    await request.set_answer(unique_appeal_id)
    await state.set_state(FSMSupport.admin)


@router.callback_query(F.data.startswith('users_admin'))
async def users_administration(callback: CallbackQuery):
    await callback.message.edit_text(text='Выберите опцию')
    await callback.message.edit_reply_markup(reply_markup=admin_ban_unban_keyboard)
    await callback.answer()


@router.callback_query(F.data == 'admin_ban')
async def admin_enter_ban_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Введите id пользователя, которого хотите забанить')
    await state.set_state(FSMSupport.admin_enter_ban)
    await callback.answer()


@router.message(StateFilter(FSMSupport.admin_enter_ban))
async def admin_ban(message: Message, request: Request, state: FSMContext):
    try:
        await request.ban_user(int(message.text))
        await message.answer("Пользователь забанен")
    except Exception as e:
        print(e)
        await message.answer("Введён некорректный id, повторите попытку")
    await state.set_state(FSMSupport.admin)


@router.callback_query(F.data == 'admin_unban')
async def admin_enter_ban_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Введите id пользователя, которого хотите разбанить')
    await state.set_state(FSMSupport.admin_enter_unban)
    await callback.answer()


@router.message(StateFilter(FSMSupport.admin_enter_unban))
async def admin_ban(message: Message, request: Request, state: FSMContext):
    try:
        await request.ban_user(int(message.text))
        await message.answer("Пользователь разбанен")
    except Exception as e:
        print(e)
        await message.answer("Введён некорректный id, повторите попытку")
    await state.set_state(FSMSupport.admin)
