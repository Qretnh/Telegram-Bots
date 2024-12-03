from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Any
from settings.prices import set_prices

price_RUB, price_USD = set_prices()

menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💴 Оплатить доступ",
                          callback_data='pay')
     ],
    [InlineKeyboardButton(text="🔍 Подробнее о канале",
                          callback_data='info')
     ],
    [InlineKeyboardButton(text="❓ F.A.Q",
                          callback_data='F.A.Q.')
     ]
])

faq_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✔️ Проверить подписку',
                          callback_data='check_subscription')]
])

enter_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="▶️ Вступить",
                          callback_data='pay')]])


def time_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"1 месяц - {price_RUB['1 month']} рублей",
                              callback_data='months|1')],
        [InlineKeyboardButton(text=f"6 месяца - {price_RUB['6 month']} рублей",
                              callback_data='months|6')],
        [InlineKeyboardButton(text=f"12 месяцев - {price_RUB['12 month']} рублей",
                              callback_data='months|12')],
    ])
    return keyboard


def payments_keyboard(months: Any):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Крипта (Cryptobot)",
                              callback_data=f'payment_Cryptobot|{str(months)}')],
        [InlineKeyboardButton(text="🤖 Крипта (Перевод)",
                              callback_data=f'payment_Cryptomus|{str(months)}')],
        [InlineKeyboardButton(text="💳 Банковская карта (YooMoney)",
                              callback_data=f'payment_YooMoney|{str(months)}')]
    ])
    return keyboard

def pay_cryptomus_keyboard(invoice):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить",
                              url=invoice.url)]
    ])
    return keyboard

def pay_cryptobot_keyboard(invoice):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить",
                              url=invoice.bot_invoice_url)]
    ])
    return keyboard


def approve_member_keyboard(link: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти",
                              url=link,
                              callback_data="approve")]])
    return keyboard
