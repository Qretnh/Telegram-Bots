import operator
import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User

from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Checkbox, ManagedCheckbox, Multiselect
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Multi

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from environs import Env

from middlewares import DbSessionMiddleware, BanMiddleware

from dialogs.user_dialogs import router as start_router, dialog as user_dialogs

import logging

from database.db import Base

env = Env()
env.read_env()

BOT_TOKEN = env('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def main():
    logger = logging.getLogger(__name__)

    dp = Dispatcher()

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    #engine = create_async_engine('', echo=False)

    #Sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    #async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)

    #    await connection.run_sync(Base.metadata.create_all)

        # await base_init(sessionmaker=Sessionmaker)

    #dp.update.outer_middleware(DbSessionMiddleware(Sessionmaker))
    #dp.update.middleware(BanMiddleware())

    dp.include_router(start_router)
    dp.include_router(user_dialogs)

    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
