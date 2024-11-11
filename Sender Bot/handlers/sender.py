from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Router, F
from aiogram.filters import CommandObject, Command, StateFilter
from aiogram.fsm.context import FSMContext
from utils.sender_state import Steps
from utils.sender_list import SenderList
from config_data.config import config
from keyboards.keyboards import answer_markup
from utils.dbconnect import Request

router = Router()


@router.message(Command(commands='start'))
async def start(message: Message, request: Request):
    await request.add_data(message.from_user.id, message.from_user.first_name)
    await message.answer('/sender название рассылки')


@router.message(Command(commands='sender', magic=F.args), F.chat.id == config.tg_bot.admin_ids[0])
async def get_sender(message: Message, command: CommandObject, state: FSMContext):
    if not command.args:
        await message.answer(f'Для создания рассылки введи команду /sender и имя рассылки')
        return

    await message.answer(f'Приступаем к рассылке. Имя кампании - {command.args}\r\n\r\n'
                         f'Отправь мне сообщение, которое будет использовано, как рекламное')

    await state.update_data(name_camp=command.args)
    await state.set_state(Steps.get_message)


@router.message(StateFilter(Steps.get_message))
async def get_message(message: Message, state: FSMContext):
    await state.update_data(message_id=message.message_id,
                            chat_id=message.from_user.id)

    await message.answer(f"Сообщение для рассылки принято.\n\n"
                         f"Нужно ли добавить кнопку",
                         reply_markup=answer_markup)

    await state.set_state(Steps.q_button)


@router.callback_query(StateFilter(Steps.q_button))
async def q_button(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    if callback.data == 'add_button':
        await callback.message.answer(f'Введите текст для кнопки:')
        await state.set_state(Steps.get_text_button)
    else:
        data = await state.get_data()
        message_id = int(data.get('message_id'))
        chat_id = int(data.get('chat_id'))
        await state.set_state(Steps.confirm)
        await confirm(callback.message, bot, message_id, chat_id, reply_markup=None)
    await callback.answer()


@router.message(StateFilter(Steps.get_text_button))
async def get_text_button(message: Message, state: FSMContext):
    await state.update_data(text_button=message.text)
    await message.answer("Отправьте ссылку для кнопки")
    await state.set_state(Steps.get_link_button)


@router.message(StateFilter(Steps.get_link_button))
async def get_link_button(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(link_button=message.text)
    sender_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=(await state.get_data()).get('text_button'),
                url=message.text)
        ]
    ])
    data = await state.get_data()
    message_id = int(data.get('message_id'))
    chat_id = int(data.get('chat_id'))
    await confirm(message, bot, message_id, chat_id, sender_keyboard)


async def confirm(message: Message, bot: Bot, message_id: int, chat_id: int, reply_markup: InlineKeyboardMarkup = None):
    await bot.copy_message(chat_id, chat_id, message_id, reply_markup=reply_markup)
    await message.answer(text="Подтвердить рассылку?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [
                                 InlineKeyboardButton(text="Да",
                                                      callback_data="confirm_sender"),
                                 InlineKeyboardButton(text="Нет",
                                                      callback_data="discard_sender")
                             ]
                         ]))


@router.callback_query(F.data == 'discard_sender')
@router.callback_query(F.data == 'confirm_sender')
async def sender_decide(callback: CallbackQuery, bot: Bot, state: FSMContext, request: Request, senderlist: SenderList):
    data = await state.get_data()
    message_id = data.get('message_id')
    chat_id = data.get('chat_id')
    text_button = data.get('text_button')
    link_button = data.get('link_button')
    name_camp = data.get('name_camp')

    if callback.data == 'confirm_sender':
        await callback.message.edit_text('Рассылка запущена...',
                                         reply_markup=None)
        if not await request.check_table(name_camp):
            await request.create_table(name_camp)
        count = await senderlist.broadcaster(name_camp, chat_id, message_id, text_button, link_button)
        await callback.message.answer(text=f'Рассылка успешно запущена, отправлено {count} сообщений ')
        await request.delete_table(name_camp)

    if callback.data == 'discard_sender':
        await callback.message.edit_text('Рассылка отменена',
                                         reply_markup=None)

    await state.clear()


async def func(message: Message):
    await message.answer('x3')
