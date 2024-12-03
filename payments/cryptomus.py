import asyncio
import datetime
import json, hashlib, base64
import time
from typing import Any

from aiohttp import ClientSession

MERCHANT_UUID: str  # айди мерчанта (тг канала, шопа)
API_KEY: str  # ключ пополнения


def generate_headers(data: str):
    sign = hashlib.md5(
        base64.b64encode(data.encode('ascii')) + API_KEY.encode('ascii')
    ).hexdigest()
    return {"merchant": MERCHANT_UUID, "sign": sign, "content-type": "application/json"}


async def create_invoice_cryptomus(user_id: int, value: float, currency: str):
    async with ClientSession() as session:
        data = {
            "amount": str(round(value, 2)),
            "order_id": f'{user_id}_{str(time.time_ns())}',
            "currency": "USDT",
            # "currencies": ["USDT", "BTC", "ETH", "SOL"],
            "lifetime": "1200",
            "to_currency": currency
        }
        json_dumps = json.dumps(data)
        response = await session.post(
            "https://api.cryptomus.com/v1/payment",
            data=json_dumps,
            headers=generate_headers(json_dumps)
        )
        return await response.json()


async def get_invoice_cryptomus(uuid: str):
    async with ClientSession() as session:
        json_dumps = json.dumps({"uuid": uuid})
        response = await session.post(
            "https://api.cryptomus.com/v1/payment/info",
            data=json_dumps,
            headers=generate_headers(json_dumps)
        )
        return await response.json()
