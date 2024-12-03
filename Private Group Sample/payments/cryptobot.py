from aiocryptopay import AioCryptoPay, Networks
from settings.tokens import *

CRYPTOBOT_API_TOKEN = set_tokens()["cryptobot"]

crypto = AioCryptoPay(token=CRYPTOBOT_API_TOKEN, network=Networks.MAIN_NET)


async def cryptobot_create_invoice(amount: int):
    return await crypto.create_invoice(amount,
                                       asset="USDT",
                                       description="Оплата подписки",
                                       expires_in=600)


async def cryptobot_get_invoice(id):
    status = await crypto.get_invoices(invoice_ids=id)
    return status
