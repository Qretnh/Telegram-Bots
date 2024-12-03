from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest
from aiogram import Bot, Router, F
from aiogram.filters import CommandObject, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from config_data.config import config
from keyboards.user_keyboards import *
from payments.cryptomus import create_invoice_cryptomus, get_invoice_cryptomus
from payments.cryptobot import cryptobot_create_invoice, cryptobot_get_invoice
from settings.prices import set_prices
from database.database import DB

import asyncio

admin_chat_id = config.tg_bot.admin_ids[0]

price_RUB, price_USD = set_prices()

router = Router()
chat_id = -1002457858447


@router.message(Command(commands=['start']))
async def start(message: Message):
    await message.answer('Приветствую 👋 Этот бот поможет тебе попасть в канал "Private".\n'
                         'Подписка - ежемесячная, оплату принимаем в валюте и крипте.\n'
                         'Отписаться можно в любой момент 🤝',
                         reply_markup=menu_keyboard)
    await DB.add_user(message.from_user.id)


@router.callback_query(F.data == 'info')
async def info(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('В Private ты найдёшь самую актуальную информацию, уникальный контент и '
                                  'много дополнительных плюшечек',
                                  reply_markup=enter_keyboard)


@router.callback_query(F.data == 'pay')
async def time(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(text='Выберите длительность подписки',
                                  reply_markup=time_keyboard())


@router.callback_query(F.data.startswith('months'))
async def pay(callback: CallbackQuery):
    months = callback.data.split("|")[1]
    await callback.answer()
    await callback.message.answer(text='Выберите способ оплаты',
                                  reply_markup=payments_keyboard(months=months))


@router.callback_query(F.data.startswith('payment_Cryptobot'))
async def payment_cryptobot(callback: CallbackQuery, bot: Bot):
    months = int(callback.data.split("|")[1])
    invoice = await cryptobot_create_invoice(price_USD[f'{months} month'])
    id = invoice.invoice_id
    await callback.answer()
    await callback.message.answer("Для перехода к оплате нажмите на кнопку. Ссылка актуальна 10 минут\n"
                                  "(Ответ от бота придёт в течение ~1 минуты после оплаты)",
                                  reply_markup=pay_cryptobot_keyboard(invoice))

    link_request = await bot.create_chat_invite_link(chat_id, "approve", creates_join_request=True)
    link_request = link_request.invite_link
    i = 0
    while i < 20:
        status = await cryptobot_get_invoice(id)
        status = status.status
        if status == "paid":
            await callback.message.answer(text="Оплата прошла успешно. Вы добавлены в канал",
                                          reply_markup=approve_member_keyboard(link_request))
            await DB.update_user_subscription(callback.from_user.id, months)
            break
        i += 1
        await asyncio.sleep(30)


@router.callback_query(F.data.startswith('payment_Cryptomus'))
async def payment_Cryptomus(callback: CallbackQuery, bot: Bot):
    months = int(callback.data.split("|")[1])
    invoice = await create_invoice_cryptomus(callback.from_user.id, int(price_USD[f'{months} month']), 'USDT')
    print(invoice)
    id = invoice.invoice_id
    await callback.answer()
    await callback.message.answer("Для перехода к оплате нажмите на кнопку. Ссылка актуальна 10 минут\n"
                                  "(Ответ от бота придёт в течение ~1 минуты после оплаты)",
                                  reply_markup=pay_cryptomus_keyboard(invoice))

    link_request = await bot.create_chat_invite_link(chat_id, "approve", creates_join_request=True)
    link_request = link_request.invite_link
    i = 0
    while i < 20:
        status = await get_invoice_cryptomus()
        status = status.status
        if status == "paid":
            await callback.message.answer(text="Оплата прошла успешно. Вы добавлены в канал",
                                          reply_markup=approve_member_keyboard(link_request))
            await DB.update_user_subscription(callback.from_user.id, months)
            break
        i += 1
        await asyncio.sleep(30)


@router.callback_query(F.data == "F.A.Q.")
async def faq(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await callback.message.answer(
        text='Здесь вы можете найти ответы на самые частые вопросы, а также проверить статус подписки',
        reply_markup=faq_keyboard)


@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery, bot: Bot):
    link_request = await bot.create_chat_invite_link(chat_id, "approve", creates_join_request=True)
    link_request = link_request.invite_link
    info = await DB.get_user_info(callback.from_user.id)
    if info:
        await callback.answer()
        await callback.message.edit_text(
            text=f"Статус вашей подписки на данный момент:\n{'❌ Не оплачена' if info[2] == 'NO' else '✅ Оплачена. Действует до: ' + info[3]}",
            reply_markup=approve_member_keyboard(link_request) if info[2] == 'YES' else None)


@router.chat_join_request()
async def check_request(request: ChatJoinRequest, bot: Bot):
    info = await DB.get_user_info(request.from_user.id)
    if info[2] == "YES":
        try:
            await bot.unban_chat_member(chat_id=chat_id,
                                        user_id=request.from_user.id)
        finally:
            await bot.approve_chat_join_request(chat_id=chat_id,
                                                user_id=request.from_user.id)


async def last_day_subscription(bot: Bot):
    users = await DB.get_users_last_day()
    for user in users:
        await bot.send_message(user,
                               text="Привет, твоя подписка заканчивается завтра\n"
                                    "Для продления выбери срок:",
                               reply_markup=time_keyboard())


async def kick_users(bot: Bot):
    users = await DB.get_users_to_remove()
    for user in users:
        try:
            await DB.remove_user_subscription(user)
            await bot.send_message(user, text="поки поки")
            await bot.ban_chat_member(chat_id, user)
            await asyncio.sleep(1)
            await bot.unban_chat_member(chat_id, user)
        finally:
            await asyncio.sleep(1)
