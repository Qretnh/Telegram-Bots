from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from config_data import config as cfg
from handlers import user_handlers, other_handlers
from handlers.user_handlers import storage
import asyncio
import logging

logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    await bot.set_my_commands([BotCommand(command='/start', description='Начать работу с ботом'),
                               BotCommand(command='/price', description='Запросить прайс-лист'),
                               BotCommand(command='/contacts', description='Наши контакты'),
                               BotCommand(command='/delivery', description='Ответы на вопросы (Доставка, контакты)')])


async def start():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config = cfg.load_config(r'C:\Users\Oren-\PycharmProjects\Bots\E-book Bot\.env')
    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode='HTML'))

    dp = Dispatcher(storage=storage)

    dp.startup.register(set_bot_commands)

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start())
