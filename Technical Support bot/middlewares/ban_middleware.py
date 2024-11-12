from typing import Callable, Awaitable, Dict, Any
import asyncpg
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from utils.dbconnect import Request


class BanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler,
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        request: Request = data.get('request')
        user = data.get('event_from_user')
        check = await request.check_banned(user.id)

        if not check:
            return await handler(event, data)
