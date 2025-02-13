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
    add_record, get_master_name, get_user_records, get_admins, get_user_by_username, append_master
from dialogs.master_dialogs import FSMMaster, master_dialog
import pytz

from database.db_funcs import add_user, get_user, get_master_services, insert_service, delete_service, get_masters, \
    update_name, update_photo, update_description, set_shift, get_shift, delete_shift, get_shifts, get_shifts_today, \
    get_master_records_today, get_master_records_date


class FSMAdmin(StatesGroup):
    add_master = State()
    delete_master = State()
    check_shifts = State()
    users_info = State()
    get_users = State()
    create_sender = State()
    manage_masters = State()
    menu = State()


router = Router()


def factory_master(text: str):
    if text[0] == '@' and len(text) < 30:
        return text
    else:
        raise ValueError


async def add_master(button: Button,
                     dialog_manager: DialogManager, text: str, **kwargs):
    session = dialog_manager.middleware_data['session']
    user_id = await get_user_by_username(username=text[1:], session=session)
    if user_id:
        await append_master(user_id, session)


async def getter_masters(dialog_manager: DialogManager,
                         **kwargs):
    session = dialog_manager.middleware_data['session']
    masters = await get_masters(session)
    masters = [(master.user_id, master.name, master.photo, master.description) for master in masters]
    return {'masters': masters}


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


admin_dialog = Dialog(
    Window(
        Const("Админ панель"),
        SwitchTo(Const("Управление мастерами"),
                 id='manage_masters',
                 state=FSMAdmin.manage_masters),
        SwitchTo(Const("Создать рассылку"),
                 id='create_sender',
                 state=FSMAdmin.create_sender),
        SwitchTo(Const("Выгрузить пользователей"),
                 id='get_users_xls',
                 state=FSMAdmin.get_users),
        SwitchTo(Const("Забанить/разбанить пользователя"),
                 id='users_info',
                 state=FSMAdmin.users_info),
        state=FSMAdmin.menu
    ),
    Window(Format("Мастера:"),
           List(Format('<a href="tg://user?id={item[0]}">{item[1]}</a>'),
                items='masters'),
           SwitchTo(Format("Добавить мастера"),
                    id='admin_add_master',
                    state=FSMAdmin.add_master),
           SwitchTo(Format("Удалить мастера"),
                    id='admin_delete_master',
                    state=FSMAdmin.delete_master),
           SwitchTo(Format("Посмотреть смены"),
                    id='admin_check_shifts',
                    state=FSMAdmin.check_shifts),
           getter=getter_masters,
           state=FSMAdmin.manage_masters
           ),
    Window(Format("Введите имя пользователя в формате @username\n"
                  "Например: @Aaaar05"),
           TextInput(id='master_input',
                     type_factory=factory_master,
                     on_success=add_master),
           state=FSMAdmin.add_master
           ),
    getter=getter
)
