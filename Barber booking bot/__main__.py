import operator
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from middlewares.ban_middleware import BanMiddleware

scheduler = AsyncIOScheduler()
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

from dialogs.master_dialogs import master_dialog
from dialogs.user_dialogs import router as start_menu, start_dialog, register_dialog
from dialogs.admin_dialogs import admin_dialog
from environs import Env
from middlewares.session import DbSessionMiddleware
import logging
from database.db import Base
from database.db_funcs import base_init

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

    engine = create_async_engine('sqlite+aiosqlite:///database.db', echo=False)

    Sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as connection:
        # Если ловите ошибку "таблица уже существует",
        # раскомментируйте следующую строку:
        # await connection.run_sync(Base.metadata.drop_all)

        await connection.run_sync(Base.metadata.create_all)

        # await base_init(sessionmaker=Sessionmaker)

    dp.update.outer_middleware(DbSessionMiddleware(Sessionmaker))
    dp.update.middleware(BanMiddleware())

    dp.include_router(start_menu)
    dp.include_router(start_dialog)
    dp.include_router(register_dialog)

    dp.include_router(master_dialog)

    dp.include_router(admin_dialog)
    setup_dialogs(dp)

    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
