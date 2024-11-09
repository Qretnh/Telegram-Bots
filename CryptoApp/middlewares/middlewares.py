from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class LanguageMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        if 'language' not in data.keys():
            storage_data = await data['state'].get_data()
            if 'language' not in storage_data.keys():
                data['language'] = 'EN'
            else:
                data['language'] = storage_data['language']

        if data['raw_state'] == 'FSMAuth:banned':
            return
        else:
            result = await handler(event, data)
            return result
