from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.db_funcs import get_banned_users


class BanMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        session = data['session']
        banned_users = await get_banned_users(session)
        try:
            user_id = event.__dict__['message'].chat.id
            if user_id in banned_users:
                return
            else:
                return await handler(event, data)
        except AttributeError:
            return await handler(event, data)