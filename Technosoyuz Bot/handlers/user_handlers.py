from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter
from keyboards.price_keyboards import generate_price_keyboard, send_number_keyboard
from services.business_logic import get_name_from_callback
from aiogram.types import callback_query
from db.user_contacts import users_contacts
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, Redis

redis = Redis(host='localhost')

storage = RedisStorage(redis=redis)


class FSMInfo(StatesGroup):
    start_bot = State()
    send_number = State()


router = Router()


@router.message(Command(commands=['start']))
async def command_start(message: Message, state: FSMContext):
    user = {}
    user = await state.get_data()
    #print(user)
    await message.answer(
        text='Здравствуйте, это бот фирмы техносоюз.\n\n'
             '/price - <b>Ознакомиться с актуальным прайс-листом</b>\n'
             '/contacts - Наши контакты\n'
             f'/delivery - Условия доставки, ответы на вопросы')


@router.message(Command(commands=['delivery']))
async def faq(message: Message):
    await message.answer_photo(photo='https://tehnosoyus.ru/img/deliveri/17.png',caption='Доставка по городу:'
                                                                                         '🟨 - 400 рублей\n'
                                                                                         '🟦 - 500 рублей\n'
                                                                                         '🟥 - 400 рублей\n'
                                                                                         '*При заказе от 2-х '
                                                                                         'баллонов. Возможность '
                                                                                         'доставки одного уточните у '
                                                                                         'менеджера')


@router.message(Command(commands=['contacts']))
async def our_contacts(message: Message):
    await message.answer(text='Наши контакты:\n\n'
                              'Адрес: г.Оренбург, пр.Автоматики 10E\n'
                              'Телефоны: +7(353)254-24-63\n'
                              'E-mail: tehnosoyuz.oren@mail.ru\n\n'
                              'Время работы: \n'
                              'пн-пт – с 9.00 до 18.00\n'
                              'сб: 9.00 - 13.00\n'
                              'без перерыва на обед')


@router.message(Command(commands=['price']), StateFilter(FSMInfo.send_number))
async def price_list_m(message: Message):
    await message.answer(text='Вот актуальный прайс-лист. Можете перейти в категории, нажав на кнопку',
                         reply_markup=generate_price_keyboard())


@router.message(Command(commands=['price']), ~StateFilter(FSMInfo.send_number))
async def price_list_m(message: Message):
    await message.answer(text='Для доступа к прайсу нажмите кнопку ниже',
                         reply_markup=send_number_keyboard())


@router.message(F.content_type == ContentType.CONTACT)
async def get_contact(message: Message, bot: Bot, state=FSMContext):
    id = message.from_user.id
    number = message.contact.phone_number
    #print(id)
    await bot.send_message(chat_id=809160060,text=f'Телефон нового клиента: {number}')
    await state.update_data(id=message.contact.phone_number)
    await state.set_state(FSMInfo.send_number)
    await message.answer(text='Благодарим вас!',
                         reply_markup=None)
    await message.answer(text='Вот актуальный прайс-лист. Можете перейти в категории, нажав на кнопку',
                         reply_markup=generate_price_keyboard())


@router.callback_query(F.data.endswith('5'))
async def return_position(callback: CallbackQuery):
    await callback.message.edit_text(text=get_name_from_callback(callback), reply_markup=None)


@router.callback_query(F.data == 'back_to_price')
async def price_list_c(callback: CallbackQuery):
    await callback.message.edit_text(text='Вот актуальный прайс-лист. Можете перейти в категории, нажав на кнопку',
                                     reply_markup=generate_price_keyboard())


@router.callback_query()
async def command_start(callback: CallbackQuery):
    await callback.message.edit_text(text=get_name_from_callback(callback),
                                     reply_markup=generate_price_keyboard(callback))
