from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from config_data import config as cfg
import aiogram.types as types

config = cfg.load_config(r'.env')


class FSM(StatesGroup):
    pin_scan = State()
    pin_number = State()


storage = MemoryStorage()
router = Router()


@router.message(CommandStart())
async def start(message: Message, bot: Bot):
    try:
        start_photo = types.FSInputFile('start_photo.png')
        await bot.send_photo(
            photo=start_photo,
            chat_id=message.from_user.id,
            caption="Здравствуйте! Рады вас приветствовать в боте магазина Supershop\n\nУ нас вы всегда можете найти самые лучшие товары по выгодным ценам")
    except:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Здравствуйте! Рады вас приветствовать в боте магазина Supershop\n\nУ нас вы всегда можете найти самые лучшие товары по выгодным ценам")

    await bot.send_message(
        text="Вы можете оставить отзыв о нас и мы подарим вам 300 рублей в благодарность за ваш отзыв!\n\n"
             "Это можно сделать по ссылке: https://www.wildberries.ru/",
        chat_id=message.from_user.id,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Я уже оставил/а отзыв😊",
                                                                                 callback_data="go_pin")]]))


@router.callback_query(F.data == "go_pin")
async def pin_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await state.set_state(FSM.pin_scan)
    photo = types.FSInputFile('example_photo.png')

    await bot.send_photo(photo=photo,
                         chat_id=callback.from_user.id,
                         caption="Пожалуйста, отправьте в чат скриншот (фото) вашего отзыва, где видно вас, оценку и текст самого отзыва☺️\n"
                                 "<b>(Пример выше)</b>")


@router.message(StateFilter(FSM.pin_scan))
async def pinned_photo(message: Message, bot: Bot, state: FSMContext):
    if message.photo:
        await state.set_state(FSM.pin_number)
        await message.reply(text="Спасибо! Сразу после проверки наш менеджер вышлет вам подарок!\n\n"
                                 "Введите пожалуйста ваш мобильный номер, чтобы мы знали куда его отправить (так же можете указать, например, банк отправки)\n\n"
                                 "Например так:\n"
                                 "+78005553535")

        await state.update_data({"photo": message.photo[-1].file_id})
        data = await state.get_data()
    else:
        await message.reply(text="Пожалуйста, прикрепите <i>фотографию</i> в чат чтобы мы могли проверить ваш отзыв")


@router.message(StateFilter(FSM.pin_number))
async def pinned_number(message: Message, bot: Bot, state: FSMContext):
    await message.reply(text="Совсем скоро ваш подарок окажется у вас😊\n\n"
                             "Спасибо, что остаётесь с нами!\n\n"
                             "Так же можете ознакомиться с нашими обновлениями ассортимента (скидка до 60%):\n"
                             "https://www.wildberries.ru/your_link")

    data = await state.get_data()
    photo = data.get('photo')
    manager_id = config.tg_bot.manager_id
    await bot.send_photo(chat_id=manager_id,
                         photo=photo,
                         caption="✅ Новый отзыв о товаре\n\n"
                                 f"✍️ Комментарий пользователя: {message.text}",
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[[InlineKeyboardButton(text="☑️ Подарок отправлен",
                                                                    callback_data="gift_sent")]]))
    await state.clear()


@router.callback_query(F.data == "gift_sent")
async def gift_sent(callback: CallbackQuery, bot: Bot):
    await callback.message.delete_reply_markup()
    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n🎁 Подарок отправлен 🎁")
    try:
        await bot.send_message(
            "Мы отправили 300 рублей по номеру, указанному вами в сообщении. Спасибо, что вы с нами!")
    finally:
        pass
