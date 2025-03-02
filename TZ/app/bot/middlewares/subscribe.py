from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from environs import Env

env = Env()
env.read_env()


async def get_banned_users():
    pass


class SubscribeMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        try:
            chat_member = await event.bot.get_chat_member("@" + env("SUBSCRIBTION_GROUP_NAME"),
                                                          data["event_context"].chat.id)
            if chat_member.status in ['member', 'administrator', 'creator']:
                return await handler(event, data)
            else:
                await event.bot.send_message(
                    text='Для продолжения необходимо подписаться на <a href="https://t.me/sdagdasgsdg">Группу</a>',
                    chat_id=data["event_context"].chat.id)
        except Exception as e:
            return await handler(event, data)

