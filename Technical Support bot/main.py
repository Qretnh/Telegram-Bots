import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from config_data.config import config
from utils.storage import storage
from handlers import user_handlers, admin_handlers
from middlewares.db_middleware import DBsession
from middlewares.ban_middleware import BanMiddleware
import asyncpg
import logging

logger = logging.getLogger(__name__)


async def create_pool():
    return await asyncpg.create_pool(user='postgres', password='qwaszx12', database='postgres',
                                     host='localhost', port=5432, command_timeout=10)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    pool_connect = await create_pool()

    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode='HTML'))

    await bot.set_my_commands([BotCommand(command='start', description='Главное меню'),
                               BotCommand(command='/support', description='Написать в поддержку')])

    dp = Dispatcher(storage=storage)
    dp.update.middleware.register(DBsession(pool_connect))
    dp.update.middleware.register(BanMiddleware())
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
