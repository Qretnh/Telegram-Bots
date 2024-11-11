import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config_data.config import config
from middlewares.dbmiddleware import DBsession
from handlers import sender
from utils.sender_list import SenderList
from utils.storage import storage
import logging
import asyncpg

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

    sender_list = SenderList(bot, pool_connect)

    dp = Dispatcher(storage=storage)
    dp.include_router(sender.router)
    dp.update.middleware.register(DBsession(pool_connect))

    await dp.start_polling(bot, senderlist=sender_list)


if __name__ == "__main__":
    asyncio.run(main())
