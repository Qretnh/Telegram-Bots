from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

offer_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Давай'), KeyboardButton(text='Не хочу')]],
                                     resize_keyboard=True, )

choose_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Камень🪨'),
                                                 KeyboardButton(text='Ножницы✂️'),
                                                 KeyboardButton(text='Бумага📄')]],
                                      resize_keyboard=True, )

wait_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Я захотел! Давай!'),
                                               KeyboardButton(text='Не хочу')]],
                                    resize_keyboard=True, )

