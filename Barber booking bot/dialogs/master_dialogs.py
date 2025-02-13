import datetime
import operator
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Checkbox, ManagedCheckbox, Multiselect, ListGroup, \
    Calendar, CalendarConfig
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Multi, List
from aiogram_dialog.widgets.kbd import SwitchTo
from environs import Env
from sqlalchemy.ext.asyncio import async_sessionmaker, async_session

from database.db_funcs import add_user, get_user, get_master_services, insert_service, delete_service, get_masters, \
    update_name, update_photo, update_description, set_shift, get_shift, delete_shift, get_shifts, get_shifts_today, \
    get_master_records_today, get_master_records_date

router = Router()


class FSMMaster(StatesGroup):
    new_shift_time = State()
    new_shift = State()
    master_shifts = State()
    profile = State()
    orders = State()
    start = State()
    services = State()

    add_service = State()
    new_length = State()
    new_desc = State()
    new_price = State()
    new_service = State()

    change_name = State()
    change_photo = State()
    change_description = State()

    change_name_enter = State()
    change_photo_enter = State()
    change_description_enter = State()

    today_books = State()
    check_books = State()
    master_books = State()
    day_books = State()


def text_check(text: str):
    if len(text) > 30:
        raise ValueError
    return text


def desc_check(text: str):
    if len(text) > 300:
        raise ValueError
    return text


def time_check(text: str):
    if text == '-':
        return "1 23"
    f, s = text.split()
    if int(f) < int(s) <= 24:
        return text
    raise ValueError


def price_check(text: str):
    if len(text) > 7:
        raise ValueError
    try:
        return int(text)
    except:
        raise ValueError


async def load_day_master(callback: CallbackQuery, widget,
                          dialog_manager: DialogManager, selected_date: datetime.date):
    pass


async def add_new_shift(callback: CallbackQuery, widget,
                        dialog_manager: DialogManager, selected_date: datetime.date):
    start_hour = dialog_manager.dialog_data['new_start_hour']
    end_hour = dialog_manager.dialog_data['new_end_hour']
    session = dialog_manager.middleware_data['session']
    shifts = await get_shift(master_id=callback.from_user.id, session=session, date=selected_date)
    if shifts == 0:
        await set_shift(master_id=callback.from_user.id, session=session, start_hour=start_hour, end_hour=end_hour,
                        date=selected_date)
        await callback.answer(f"смена установлена {str(selected_date)}")
    else:
        await delete_shift(master_id=callback.from_user.id, session=session, date=selected_date)
        await callback.answer(f"смена убрана {str(selected_date)}")


async def set_new_name(message: Message,
                       widget: ManagedTextInput,
                       dialog_manager: DialogManager,
                       text: str,
                       **kwargs):
    session = dialog_manager.middleware_data['session']
    await update_name(master_id=message.from_user.id, new_name=text, session=session)
    await dialog_manager.switch_to(FSMMaster.profile)


async def set_new_photo(message: Message,
                        widget: ManagedTextInput,
                        dialog_manager: DialogManager,
                        text: str,
                        **kwargs):
    session = dialog_manager.middleware_data['session']
    await update_photo(master_id=message.from_user.id, new_photo=text, session=session)
    await dialog_manager.switch_to(FSMMaster.profile)


async def set_new_time(message: Message,
                       widget: ManagedTextInput,
                       dialog_manager: DialogManager,
                       text: str,
                       **kwargs):
    start, end = text.split()
    dialog_manager.dialog_data.update({"new_start_hour": start})
    dialog_manager.dialog_data.update({"new_end_hour": end})
    await dialog_manager.switch_to(FSMMaster.new_shift)


async def set_new_description(message: Message,
                              widget: ManagedTextInput,
                              dialog_manager: DialogManager,
                              text: str,
                              **kwargs):
    session = dialog_manager.middleware_data['session']
    await update_description(master_id=message.from_user.id, new_description=text, session=session)
    await dialog_manager.switch_to(FSMMaster.profile)


async def add_new_service(message: Message,
                          widget: ManagedTextInput,
                          dialog_manager: DialogManager,
                          text: str, **kwargs):
    session = dialog_manager.middleware_data['session']
    new_title = dialog_manager.dialog_data["new_service_text"]
    new_price = dialog_manager.dialog_data["new_service_price"]
    new_length = dialog_manager.dialog_data["new_service_length"]
    new_desc = text
    await insert_service(master_id=message.from_user.id, session=session, title=new_title, description=new_desc,
                         length=new_length, price=new_price)
    await dialog_manager.switch_to(FSMMaster.start)


async def switch_to_len(message: Message,
                        widget: ManagedTextInput,
                        dialog_manager: DialogManager,
                        text: str, **kwargs):
    dialog_manager.dialog_data.update({"new_service_price": text})
    await dialog_manager.switch_to(FSMMaster.new_length)


async def switch_to_price(message: Message,
                          widget: ManagedTextInput,
                          dialog_manager: DialogManager,
                          text: str, **kwargs):
    dialog_manager.dialog_data.update({"new_service_text": text})
    await dialog_manager.switch_to(FSMMaster.new_price)


async def switch_to_desc(message: Message,
                         widget: ManagedTextInput,
                         dialog_manager: DialogManager,
                         text: str, **kwargs):
    dialog_manager.dialog_data.update({"new_service_length": int(text)})
    await dialog_manager.switch_to(FSMMaster.new_desc)


async def books_day(callback: CallbackQuery,
                    button: Button,
                    dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    start = dialog_manager.event.data.find(':')
    end = dialog_manager.event.data[start + 1:].find(':')
    date = dialog_manager.event.data[start + 1: start + end + 1]
    dialog_manager.dialog_data.update({'check_date': date})
    await dialog_manager.switch_to(FSMMaster.day_books)


async def rm_service(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    start = dialog_manager.event.data.find(':')
    end = dialog_manager.event.data[start + 1:].find(':')
    service_id = dialog_manager.event.data[start + 1: start + end + 1]
    await delete_service(service_id, session)


async def switch_to_services(callback: CallbackQuery,
                             button: Button,
                             dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    master_id = callback.from_user.id
    services = await get_master_services(master_id, session)
    await dialog_manager.switch_to(FSMMaster.add_service)


async def getter_shifts(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    shifts = await get_shifts(event_from_user.id, session)
    shifts = sorted(shifts, key=lambda x: x[0])
    return {"shifts": shifts}


async def getter_today_records(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    shifts = await get_master_records_today(event_from_user.id, session)
    return {"shifts": shifts}


async def getter_date_records(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    date = dialog_manager.dialog_data['check_date']
    records = await get_master_records_date(event_from_user.id, date, session)
    return {'date': date,
            'records': records}

    return {"shifts": shifts}


async def getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session = kwargs['session']
    master_id = event_from_user.id
    services = await get_master_services(master_id, session)
    services_list = [
        {
            'user_id': service.user_id,
            'price': service.price,
            'name': service.name,
            'length': service.length,
            'unique_id': service.unique_id
        }
        for service in services if service.user_id == master_id
    ]

    return {'session': session,
            'services': services_list}


async def get_masters_info(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session = kwargs['session']
    masters = await get_masters(session)
    id = event_from_user.id
    masters = [(master.user_id, master.name, master.photo, master.description) for master in masters if
               master.user_id == id]
    master_info = masters[0]
    return {'info': master_info}


async def get_username(event_from_user: User, **kwargs):
    print(event_from_user)
    return {'username': event_from_user.first_name}


master_dialog = Dialog(
    Window(
        Const('Меню мастера'),
        Button(Const('✂️ Поменять услуги'),
               id='services',
               on_click=switch_to_services),
        SwitchTo(Const('⏰ Мои смены'),
                 id='change_time',
                 state=FSMMaster.master_shifts),
        SwitchTo(Const('✏️ Мои записи'),
                 id='my_orders',
                 state=FSMMaster.master_books),
        SwitchTo(Const('👨🏼‍🦰 Изменить профиль'),
                 id='profile',
                 state=FSMMaster.profile),
        state=FSMMaster.start
    ),
    Window(
        Const("Мои услуги"),
        List(field=Format("{item[name]}: {item[price]} рублей"),
             items="services"),
        ListGroup(
            Button(Format("❌ {item[name]} "),
                   id="item",
                   on_click=rm_service),
            id='master_buttons',
            item_id_getter=lambda item: item['unique_id'],
            items="services",
        ),
        SwitchTo(Const("➕ Добавить"),
                 id='new_service',
                 state=FSMMaster.new_service),
        SwitchTo(Const("🔙 Назад"),
                 id='back_to_fsmmaster',
                 state=FSMMaster.start),
        state=FSMMaster.add_service,
    ),
    Window(
        Const("Введите название новой услуги. Не более 30 символов"),
        TextInput(id='new_service_name',
                  type_factory=text_check,
                  on_success=switch_to_price),
        state=FSMMaster.new_service
    ),
    Window(
        Const("Введите стоимость новой услуги в рублях. только цифры без пробелов\nНапример:\n1000"),
        TextInput(id='new_service_price',
                  type_factory=price_check,
                  on_success=switch_to_len),
        state=FSMMaster.new_price,
    ),
    Window(
        Const("Введите длительность новой услуги в минутах. Не более 5 символов\nНапример:\n30"),
        TextInput(id='new_service_length',
                  type_factory=price_check,
                  on_success=switch_to_desc),
        state=FSMMaster.new_length
    ),
    Window(
        Const("Введите описание новой услуги. до 300 символов. Введённый текст отобразится в описании услуги"),
        TextInput(id='new_service_desc',
                  type_factory=desc_check,
                  on_success=add_new_service),
        state=FSMMaster.new_desc,
    ),
    Window(
        Const("👤 Ваш профиль\n"),
        Format("id: {info[0]}\n"
               "Имя: {info[1]}\n"
               "Фото: {info[2]}\n"
               "О себе: {info[3]}\n"),
        SwitchTo(Const("👔 Поменять имя"),
                 id='master_change_name',
                 state=FSMMaster.change_name),
        SwitchTo(Const("📷 Поменять фото"),
                 id='master_change_photo',
                 state=FSMMaster.change_photo),
        SwitchTo(Const("📄 Поменять описание"),
                 id='master_change_desc',
                 state=FSMMaster.change_description),
        SwitchTo(Const("🔙 Назад"),
                 id='back_to_master',
                 state=FSMMaster.start),
        getter=get_masters_info,
        state=FSMMaster.profile
    ),
    Window(Const("Введите новое имя"),
           TextInput(id="master_new_name",
                     type_factory=text_check,
                     on_success=set_new_name),
           state=FSMMaster.change_name),
    Window(Const("Отправьте ссылку на новое фото"),
           TextInput(id="master_new_photo",
                     type_factory=desc_check,
                     on_success=set_new_photo),
           state=FSMMaster.change_photo),
    Window(Const("Введите текст графы 'О себе'"),
           TextInput(id="master_new_description",
                     type_factory=desc_check,
                     on_success=set_new_description),
           state=FSMMaster.change_description),
    Window(Const("Смены:"),
           List(Format("{item[0]} | с {item[1]}-{item[2]}"),
                items="shifts"),
           SwitchTo(Const("🔧 Добавить/Удалить смену"),
                    id='new_shift',
                    state=FSMMaster.new_shift_time),
           SwitchTo(Const("Назад"),
                    id="back_from_shifts",
                    state=FSMMaster.start),
           getter=getter_shifts,
           state=FSMMaster.master_shifts),
    Window(Const("Добавление новой смены\n\nДля удаления - нажмите на день с открой сменой. она закроется и не будет "
                 "отображаться как доступная для записи\n\nОткрытые смены на данный момент:"),
           List(Format("<i>{item[0]}</i> | с {item[1]}-{item[2]}"),
                items="shifts"),
           Calendar(id='new_shift',
                    on_click=add_new_shift,
                    config=CalendarConfig(min_date=datetime.date.today())),
           SwitchTo(Const("Назад"),
                    id="back_from_shifts",
                    state=FSMMaster.start),
           getter=getter_shifts,
           state=FSMMaster.new_shift),
    Window(Const("Введите через пробел от скольки до скольки вы открываете запись.\n"
                 "Если вам нужно удалить запись, то просто введите прочерк (1 символ: '-')\n"
                 "Например: 9 22\n"
                 "(В данном случае смена будет с 9:00 до 22:00)\n\n"),
           TextInput(id="master_new_shift",
                     type_factory=time_check,
                     on_success=set_new_time),
           state=FSMMaster.new_shift_time),
    Window(Const("⏰ Мои записи"),
           SwitchTo(Const("Записи на сегодня"),
                    id="today_books",
                    state=FSMMaster.today_books),
           SwitchTo(Const("Посмотреть записи на день"),
                    id="check_books",
                    state=FSMMaster.check_books),
           SwitchTo(Const("Назад"),
                    id="back_from_shifts",
                    state=FSMMaster.start),
           state=FSMMaster.master_books),
    Window(Const("Выберите день"),
           ListGroup(
               Button(Format("{item[0]}"),
                      id="x",
                      on_click=books_day),
               id='choose_day_buttons',
               item_id_getter=lambda item: item[0],
               items="shifts",
           ),
           SwitchTo(Const("Назад"),
                    id="back_from_shifts",
                    state=FSMMaster.start),
           state=FSMMaster.check_books,
           getter=getter_shifts),
    Window(Const("Записи на сегодня"),
           List(Format("\n<b>{item[0]}</b>\n<i>{item[2]}</i>"),
                items='shifts'),
           SwitchTo(Const("Назад"),
                    id="back_from_shifts",
                    state=FSMMaster.start),
           getter=getter_today_records,
           state=FSMMaster.today_books),
    Window(Format("Записи на {dialog_data[check_date]}"),
           List(Format("\n<b>{item[0]}</b>\n<i>{item[2]}</i>"),
                items='records'),
           SwitchTo(Const("Назад"),
                    id="back_from_shifts",
                    state=FSMMaster.start),
           getter=getter_date_records,
           state=FSMMaster.day_books),
    getter=getter
)
