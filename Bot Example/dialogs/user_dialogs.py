import datetime
import operator
import time

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

router = Router()


class FSM(StatesGroup):
    start = State()
    pass


dialog = Dialog(
    Window(
        Const("First window"),
        state=FSM.start
    )
)


@router.message(Command(commands=['start']))
async def command_start(message: Message, dialog_manager: DialogManager, **kwargs   ):
    await dialog_manager.start(state=FSM.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)
