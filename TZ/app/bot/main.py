import asyncio

import requests

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from aiogram_dialog import setup_dialogs

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from environs import Env

from app.bot.middlewares import DbSessionMiddleware, SubscribeMiddleware
from app.bot.dialogs.user_dialogs import router as start_router, dialog as user_dialogs

import logging

env = Env()
env.read_env()
BOT_TOKEN = env('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.set_my_commands([BotCommand(command='start', description="Стартовое меню")])


def send(user_id: int,
         message: str,
         buttons: list[str:str] = None):
    BOT_TOKEN = env("BOT_TOKEN")
    CHAT_ID = user_id
    message_text = message

    keyboard = [
        [{"text": button[0], "url": button[1]}] for button in buttons
    ] if buttons else None

    inline_keyboard = {
        "inline_keyboard": keyboard
    }

    # URL для отправки сообщения
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    if buttons:
        payload = {
            "chat_id": CHAT_ID,
            "text": message_text,
            "reply_markup": inline_keyboard
        }
    else:
        payload = {
            "chat_id": CHAT_ID,
            "text": message_text,
        }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Сообщение успешно отправлено!")
        return 1
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")
        return 0


async def main():
    dp = Dispatcher()

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    # подключение бд и создание движка для сессий
    dsn = str(env("DB_SCHEMA") + '://' + env("DB_USER") + ':' + env("DB_PASSWORD") + f'@{env("DB_PROVIDER")}/' + env(
        "DATABASE"))
    engine = create_async_engine(dsn, echo=False)
    Sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    # подключений миддлварей(проброс сессии с бд и проверка подписки)
    dp.update.outer_middleware(DbSessionMiddleware(Sessionmaker))
    dp.update.middleware(SubscribeMiddleware())

    # подключение роутеров
    dp.include_router(start_router)
    dp.include_router(user_dialogs)

    # подключение диалога aiogram_dialogs
    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)  # удаление апдейтов до запуска бота
    await dp.start_polling(bot)  # запуск бота!


if __name__ == '__main__':
    asyncio.run(main())
