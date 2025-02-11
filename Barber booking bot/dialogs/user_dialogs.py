import datetime
import operator
import time

from __main__ import scheduler
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs, ShowMode
from aiogram_dialog.widgets.kbd import Back, Next, ScrollingGroup, ListGroup, Start, Select
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Checkbox, ManagedCheckbox, Multiselect, Calendar, \
    CalendarConfig
from aiogram_dialog.widgets.media import StaticMedia, DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, Multi, List
from aiogram_dialog.widgets.kbd import SwitchTo
from environs import Env
from sqlalchemy.ext.asyncio import async_sessionmaker, async_session

from database.db_funcs import add_user, get_user, get_masters, get_master_services, get_shifts, check_records, \
    add_record, get_master_name, get_user_records, get_admins
from dialogs.admin_dialogs import FSMAdmin, admin_dialog
from dialogs.master_dialogs import FSMMaster, master_dialog
import pytz

tz = pytz.timezone('Europe/Moscow')
router = Router()


class FSMRegister(StatesGroup):
    birthdate = State()
    phone = State()


async def reg_date():
    pass


class FSMStart(StatesGroup):
    free_days = State()
    start = State()
    about_us = State()
    referral = State()
    reg = State()
    master = State()
    free_windows = State()
    end_book = State()
    my_records = State()


async def send_message_scheduled(id, bot: Bot, book_info, time):
    if time == 1:
        await bot.send_message(id, f"🔔 Напоминание 🔔\n"
                                   f"Через час у вас - {book_info['title']}\n"
                                   f"Начало в {book_info['time']}\n"
                                   f"Мастер - {book_info['master']}\n"
                                   f"Ждём вас!😊")
    if time == 24:
        await bot.send_message(id, f"🔔 Напоминание 🔔\n"
                                   f"Завтра у вас - {book_info['title']}\n"
                                   f"Начало в {book_info['time']}\n"
                                   f"Мастер - {book_info['master']}\n"
                                   f"За час до начала мы повторно отправим вам напоминание ;)")


def check_date(text: str):
    try:
        day = int(text[:2])
        month = int(text[3:5])
        year = int(text[6:10])
    except Exception as e:
        raise ValueError
    if year <= 1900 or year >= 2025:
        raise ValueError
    if day > 31:
        raise ValueError
    if month > 12:
        raise ValueError
    return text


def check_number(text: str):
    if 10 <= len(text) <= 12:
        if text.isdigit():
            return text
    raise ValueError


async def order(callback: CallbackQuery,
                widget: ManagedTextInput,
                dialog_manager: DialogManager):
    dialog_manager.dialog_data.update({"master_num": 0})
    await dialog_manager.switch_to(FSMStart.master)


async def save_date(message: Message,
                    widget: ManagedTextInput,
                    dialog_manager: DialogManager,
                    text: str, **kwargs) -> None:
    dialog_manager.dialog_data.update({'register_date': text})
    await dialog_manager.switch_to(FSMRegister.phone)


async def choose_service(callback: CallbackQuery,
                         button: Button,
                         dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    num = dialog_manager.dialog_data['master_num']
    masters = await get_masters(session)

    await dialog_manager.switch_to(FSMStart.reg)


async def save_number(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str, **kwargs) -> None:
    session = dialog_manager.middleware_data['session']
    birthdate = dialog_manager.dialog_data['register_date']
    await add_user(session, message.from_user.id, message.from_user.first_name, birthdate,
                   message.from_user.username, int(text))
    await dialog_manager.done()
    await dialog_manager.start(state=FSMStart.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)


async def switch_to_master(callback: CallbackQuery,
                           Button: Button,
                           dialog_manager: DialogManager):
    await dialog_manager.start(FSMMaster.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)


async def switch_to_admin(callback: CallbackQuery,
                          Button: Button,
                          dialog_manager: DialogManager):
    await dialog_manager.start(FSMAdmin.menu, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)


def time_intervals(start_hour, end_hour):
    intervals = []
    current_hour = start_hour

    while current_hour < end_hour:
        for minute in [0, 30]:
            if current_hour < end_hour or (current_hour == end_hour and minute == 0):
                intervals.append(f"{current_hour}:{minute:02d}")

        # Переход к следующему часу, если минуты равны 30
        if minute == 30:
            current_hour += 1

    return intervals


async def check_free_shifts(callback: CallbackQuery,
                            Button: Button,
                            dialog_manager: DialogManager):
    start = dialog_manager.event.data.find(':')
    end = dialog_manager.event.data[start + 1:].find(':')
    service_unique_id = dialog_manager.event.data[start + 1:start + end + 1]

    session = dialog_manager.middleware_data['session']
    num = dialog_manager.dialog_data.get("master_num")
    masters = await get_masters(session)
    masters = [(master.user_id, master.name, master.photo, master.description) for master in masters]
    master_id = masters[num][0]
    services = await get_master_services(master_id, session)
    service = [[service.user_id, service.price, service.name, service.length, service.unique_id] for service in
               services if
               int(service.unique_id) == int(service_unique_id)]
    shifts = await get_shifts(master_id=master_id, session=session)
    print("shifts", shifts)
    dialog_manager.dialog_data.update({'service_info': service[0]})
    dialog_manager.dialog_data.update({'available_shifts': shifts})
    await dialog_manager.switch_to(FSMStart.free_days)


async def check_free_time(callback: CallbackQuery,
                          Button: Button,
                          dialog_manager: DialogManager, item_id: str):
    service_date = item_id
    session = dialog_manager.middleware_data['session']
    num = dialog_manager.dialog_data.get("master_num")
    service = dialog_manager.dialog_data.get("service_info")
    service_len = service[3]
    masters = await get_masters(session)
    masters = [(master.user_id, master.name, master.photo, master.description) for master in masters]
    master_id = masters[num][0]

    shifts = await get_shifts(master_id=master_id, session=session)
    shift = [shift for shift in shifts if shift[0].strftime('%d-%m-%Y') == service_date][0]
    intervals = time_intervals(int(shift[1]), int(shift[2]))

    records = await check_records(master_id=master_id, date=service_date, session=session)

    actual_intervals = []
    if records:
        for interval in intervals:
            time_interval = datetime.datetime.strptime(interval, "%H:%M").time()
            end_service_time = (
                    datetime.datetime.combine(datetime.date.today(), time_interval) + datetime.timedelta(
                minutes=service_len)).time()
            flag = 1
            print('time_interval', time_interval, 'end_service_time', end_service_time)
            for record in records:

                s_time = datetime.datetime.strptime(record[0], "%H:%M").time()  # имеющаяся уже запись, её начало
                f_time = datetime.datetime.strptime(record[1], "%H:%M").time()  # имеющаяся уже запись, её конец
                print('record_start_time', s_time, 'record_end_time', f_time)
                if s_time <= time_interval < f_time or s_time <= end_service_time < f_time:
                    flag = 0
                if datetime.datetime.strptime(service_date, "%d-%m-%Y").date() == datetime.datetime.today().date():
                    if time_interval < datetime.datetime.today().time():
                        flag = 0

            if flag == 1:
                actual_intervals.append(time_interval)
    else:
        actual_intervals = intervals

    dialog_manager.dialog_data.update({"intervals": actual_intervals})
    dialog_manager.dialog_data.update({"choosed_date": service_date})
    await dialog_manager.switch_to(FSMStart.free_windows)


async def end_book_time(callback: CallbackQuery,
                        Button: Button,
                        dialog_manager: DialogManager,
                        item_id: str):
    print(dialog_manager.dialog_data)
    session = dialog_manager.middleware_data['session']
    selected_date = dialog_manager.dialog_data['choosed_date']
    master_id = dialog_manager.dialog_data['service_info'][0]
    master = await get_master_name(master_id, session)
    price = dialog_manager.dialog_data['service_info'][1]
    title_service = dialog_manager.dialog_data['service_info'][2]
    length = dialog_manager.dialog_data['service_info'][3]
    client_id = callback.from_user.id
    username = await callback.bot.get_chat(chat_id=client_id)
    book_info = {'date': selected_date,
                 'master': master,
                 'price': price,
                 'title': title_service,
                 'length': length,
                 'time': item_id}
    time_obj = datetime.datetime.strptime(item_id, '%H:%M').time()
    date_obj = datetime.datetime.strptime(selected_date, "%d-%m-%Y").date()
    datetime_obj = datetime.datetime.combine(date_obj, time_obj)
    scheduler.add_job(send_message_scheduled, trigger="date",
                      run_date=tz.localize(datetime_obj - datetime.timedelta(hours=1)),
                      args=[callback.from_user.id, callback.bot, book_info, 1])
    scheduler.add_job(send_message_scheduled, trigger="date",
                      run_date=tz.localize(datetime_obj - datetime.timedelta(hours=24)),
                      args=[callback.from_user.id, callback.bot, book_info, 24])
    await callback.bot.send_message(chat_id=master_id,
                                    text=f"🆕 Новая запись!\n{title_service}\n📆 {selected_date}\n🕔 {item_id}\n👨🏼‍🦰 <code>{username.first_name}</code>")
    await add_record(master_id=master_id, selected_date=selected_date, selected_time=item_id, length=length,
                     price=price, client_id=client_id, name=title_service, session=session)
    print(dialog_manager.dialog_data)
    dialog_manager.dialog_data.update({"book_info": book_info})
    await dialog_manager.switch_to(FSMStart.end_book)


async def next_master(callback: CallbackQuery,
                      Button: Button,
                      dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    try:
        num = dialog_manager.dialog_data.get("master_num")
    except:
        num = 0
    maximum = await get_masters(session)

    if num + 1 < len(maximum):
        dialog_manager.dialog_data.update({"master_num": num + 1})
    else:
        await callback.answer("Больше нет мастеров")

    await dialog_manager.switch_to(FSMStart.master)


async def prev_master(callback: CallbackQuery,
                      Button: Button,
                      dialog_manager: DialogManager):
    try:
        num = dialog_manager.dialog_data.get("master_num")
    except:
        num = 0
        dialog_manager.dialog_data.update({"master_num": num})
    if num > 0:
        dialog_manager.dialog_data.update({"master_num": num - 1})
        await dialog_manager.switch_to(FSMStart.master)


async def getter_is_master(dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    masters = await get_masters(session)
    masters = [master.user_id for master in masters]
    admins = await get_admins(session)
    admins = [admin.user_id for admin in admins]
    return {'is_master': dialog_manager.event.from_user.id in masters,
            'is_admin': dialog_manager.event.from_user.id in admins}


async def getter_masters(dialog_manager: DialogManager, **kwargs):
    try:
        num = dialog_manager.dialog_data.get("master_num")
    except:
        num = 0
    session = dialog_manager.middleware_data['session']
    masters = await get_masters(session)
    masters = [(master.user_id, master.name, master.photo, master.description) for master in masters]
    print('num=', num, ' master_id=', masters[num][0], '\n', masters)
    master_id = masters[num][0]

    services = await get_master_services(master_id, session)
    services = [(service.user_id, service.price, service.name, service.length, service.unique_id) for service in
                services if
                service.user_id == master_id]

    photo = MediaAttachment(type=ContentType.PHOTO, url=masters[num][2])
    return {'masters': masters[num],
            'photo': photo,
            'services': services}


async def getter_shifts(dialog_manager: DialogManager, **kwargs):
    shifts = dialog_manager.dialog_data['available_shifts']
    shifts = sorted([shift[0].strftime('%d-%m-%Y') for shift in shifts])
    return {'shifts': shifts}


async def getter(dialog_manager: DialogManager, **kwargs):
    session = kwargs['session']

    return {'session': session}


async def getter_intervals(dialog_manager: DialogManager, **kwargs):
    intervals = dialog_manager.dialog_data['intervals']
    intervals = [f"{interval.hour}:{interval.minute:02}" if type(interval) != str else interval for interval in
                 intervals]
    print('getter_intervals', intervals)
    return {'intervals': intervals}


async def getter_user_records(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    records = await get_user_records(dialog_manager.event.from_user.id, session=session)
    print(records)
    return {'records': records}


# Это геттер
async def get_username(event_from_user: User, **kwargs):
    print(event_from_user)
    return {'username': event_from_user.first_name}


start_dialog = Dialog(
    Window(
        Const(text='<b>Добро пожаловать в ✂️EXABARBERSHOP✂️ bot</b>\n\n'
                   'Этот бот создан как пример для отображения базового функционала бота-барбершопа.\n\n'
                   'Для навигации воспользуйтесь кнопками ниже:', ),
        Button(Const('💇🏻‍♂️ Записаться'),
               id='choose_service',
               on_click=order),
        SwitchTo(Const('💈 О нас'),
                 id='about_us',
                 state=FSMStart.about_us),
        SwitchTo(Const('📆 Мои записи'),
                 id='my_records',
                 state=FSMStart.my_records),
        SwitchTo(Const('🤝 Реферальная программа'),
                 id='referral',
                 state=FSMStart.referral),
        Button(Const("💇🏼 Меню мастера"),
               id='master_menu',
               on_click=switch_to_master,
               when='is_master'),
        Button(Const("🌟 Меню админа"),
               id='admin_menu',
               on_click=switch_to_admin,
               when='is_admin'),
        state=FSMStart.start,
        getter=getter_is_master
    ),
    Window(
        Const("▎💈 О нас \n\n"
              "Добро пожаловать в Мужской Барбершоп 'EXABARBER'!\n\n"
              "Мы — команда профессиональных барберов, работающих с 2018 года, и наша цель — помочь каждому мужчине выглядеть стильно и уверенно. \n\n"
              "📍 Наша локация:\n"
              "Адрес: ул. Примерная, 123, г. Москва \n"
              "Уютный интерьер и атмосфера, где каждый клиент чувствует себя как дома.\n\n"
              "⏰ Часы работы:\n"
              "Пн-Пт: 10:00 - 20:00\n"
              "Сб: 10:00 - 18:00 \n"
              "Вс: Выходной \n\n"
              "📞 Как с нами связаться: \n"
              "Телефон: +7 (123) 456-78-90"),
        SwitchTo(Const('🔙 Назад'),
                 id='back_from_about',
                 state=FSMStart.start),
        state=FSMStart.about_us
    ),
    Window(
        Const("Выберите мастера\n"),
        Format("🌟 Мастер: {masters[1]}\n\n🖋 О себе: \n{masters[3]}\n\n✂️ Услуги:"),
        List(field=Format("{item[2]}: {item[1]} рублей"),
             items="services"),
        DynamicMedia("photo"),
        Row(
            Button(Const("<<"),
                   id='prev_master',
                   on_click=prev_master),
            SwitchTo(Const('🔙 Назад'),
                     id='back_from_about',
                     state=FSMStart.start),
            Button(Const(">>"),
                   id='next_master',
                   on_click=next_master)
        ),
        Button(Const("💇🏻‍♂️ Выбрать услугу"),
               id="choose_service",
               on_click=choose_service),
        state=FSMStart.master,
        getter=getter_masters
    ),

    Window(
        Const("Выберите услугу:\n"),
        List(field=Format("{item[2]}: {item[1]} рублей"),
             items="services"),
        ListGroup(
            Button(Format("{item[2]}"),
                   id="x",
                   on_click=check_free_shifts),
            id='master_buttons',
            item_id_getter=lambda item: item[4],
            items="services",
        ),
        SwitchTo(Const('🔙 Назад'),
                 id='back_from_about',
                 state=FSMStart.master),
        state=FSMStart.reg,
        getter=getter_masters
    ),
    Window(
        Const("Выберите подходящий вам день для записи\n"),
        ScrollingGroup(
            Select(Format("{item}"),
                   on_click=check_free_time,
                   id='shifts_buttons',
                   item_id_getter=lambda item: item,
                   items="shifts", ),

            width=2,
            height=4,
            id='sc_gr',
        ),
        SwitchTo(Const('🔙 Назад'),
                 id='back_from_shifts',
                 state=FSMStart.master),
        getter=getter_shifts,
        state=FSMStart.free_days
    ),
    Window(
        Const("Выберите подходящее время для записи\n"),
        ScrollingGroup(
            Select(
                Format("{item}"),
                on_click=end_book_time,
                id='intervals_button',
                item_id_getter=lambda item: item,
                items="intervals",
            ),
            width=1,
            height=4,
            id='in_gr',
        ),
        SwitchTo(Const('🔙 Назад'),
                 id='back_from_int',
                 state=FSMStart.reg),
        getter=getter_intervals,
        state=FSMStart.free_windows
    ),

    Window(
        Format("✅ Ваша запись {dialog_data[book_info][date]}\n\n"
               "{dialog_data[book_info][title]}\n"
               "Время: {dialog_data[book_info][time]}\n"
               "Длительность: {dialog_data[book_info][length]} минут\n"
               "Мастер: {dialog_data[book_info][master]}\n"
               "Цена: {dialog_data[book_info][price]} рублей"),
        state=FSMStart.end_book
    ),
    Window(
        Format("Актуальные записи\n"),
        List(Format("📅 {item[4]}\n💈 {item[0]}\n🕘 Время: {item[1]}\n⏳ Длительность: {item[2]}\n💇🏼 Мастер: {item[3]}"),
             items='records',
             sep='\n\n'),
        SwitchTo(Const('🔙 Назад'),
                 id='back_from_about',
                 state=FSMStart.start),
        getter=getter_user_records,
        state=FSMStart.my_records
    )

)

register_dialog = Dialog(
    Window(
        Const("Вы у нас впервые?\n\n"
              "Пройдём короткое знакомство - введите вашу дату рождения. Это нужно, чтобы вы получали предложения о наших акциях!\n\n"
              "Формат ввода: ДД.ММ.ГГГГ (например: 11.01.2001)"),
        TextInput(
            id='birthdate_input',
            type_factory=check_date,
            on_success=save_date
        ),
        state=FSMRegister.birthdate
    ),
    Window(
        Const("Спасибо! И последнее:\n\n"
              "Введите номер вашего телефона, без +, скобок и разделителей\n\n"
              "Пример: 7911008405"),
        TextInput(id='phone_input',
                  type_factory=check_number,
                  on_success=save_number),
        state=FSMRegister.phone
    ),
    getter=getter

)


# Это классический хэндлер, который будет срабатывать на команду /start
@router.message(Command(commands=['start']))
async def command_start_process(message: Message, dialog_manager: DialogManager, session: async_session):
    result = await get_user(session=session,
                            id=message.from_user.id,
                            username=message.from_user.first_name)
    if len(result) == 0:
        await dialog_manager.start(state=FSMRegister.birthdate, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)
    else:
        try:
            await dialog_manager.done()
        except:
            pass
        await dialog_manager.start(state=FSMStart.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)
