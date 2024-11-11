from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

answer_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Да', callback_data='add_button'),
                                                       InlineKeyboardButton(text='Нет', callback_data='no_button')]])