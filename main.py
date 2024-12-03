import asyncio
import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config_data.config import config
from handlers.admin_handlers import router as admin_handlers
from handlers.user_handlers import router as user_handlers
from handlers.user_handlers import last_day_subscription, kick_users
from settings.prices import set_prices
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import logging

logger = logging.getLogger(__name__)
storage = MemoryStorage()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode='HTML'))

    await bot.set_my_commands([BotCommand(command='start', description='Главное меню'),
                               BotCommand(command='/support', description='Написать в поддержку')])

    dp = Dispatcher()
    dp.include_router(user_handlers)
    dp.include_router(admin_handlers)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(last_day_subscription, trigger='interval',
                      days=1,
                      kwargs={'bot': bot})
    scheduler.add_job(kick_users, trigger='interval',
                      seconds=100,
                      kwargs={'bot': bot})
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
