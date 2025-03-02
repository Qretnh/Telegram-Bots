from environs import Env
from aiogram import Bot
from aiogram.types import LabeledPrice

env = Env()
env.read_env()


async def order(chat_id: int,
                bot: Bot,
                products: str,
                total_price: int):
    await bot.send_invoice(
        chat_id=chat_id,
        title="Покупка техники через телеграм-бот",
        description="Описание",
        payload=products,
        provider_token=env("YOUKASSA_TOKEN"),
        currency='rub',
        prices=[
            LabeledPrice(
                label=products,
                amount=int(total_price) * 100
            )
        ],
        need_email=True,  # потребовать почту
        need_name=True,  # потребовать имя
        need_phone_number=True,  # потребовать мобильный номер
        need_shipping_address=True, # потребовать адрес
        disable_notification=False, # оставить уведомления
        request_timeout=600,
    )
