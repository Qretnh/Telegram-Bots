from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from core.handlers.basic import get_start
from core.settings import settings
import asyncio
import logging


async def start_bot(bot: Bot):
    print('|бот запущен успешно|')


async def stop_bot(bot: Bot):
    print('|бот завершил свою работу успешно|')


async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                        )
    bot = Bot(token=settings.bots.bot_token,
              default=DefaultBotProperties(parse_mode='HTML'))

    dp = Dispatcher()

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    dp.message.register(get_start)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
