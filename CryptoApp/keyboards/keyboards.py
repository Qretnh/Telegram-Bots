from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon import lexicon
from services.banks import russia_banks
from services.menu import menu_buttons
from random import randint

choose_language_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Русский🇷🇺', callback_data='RU'),
                      InlineKeyboardButton(text='English🇺🇸', callback_data='EN')]],
    resize_keyboard=True)

russia_banks_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text=bank, callback_data=bank) for bank in russia_banks]]
)


def get_countries_keyboard(language: str):
    countries = lexicon['countries'][language]
    buttons = [InlineKeyboardButton(text=country, callback_data=country) for country in countries]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def generate_captcha_keyboard(second_try: bool = False):
    captcha_variants = [
        ['50+2', InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='54', callback_data=("Ban" if second_try else "Stop")),
                              InlineKeyboardButton(text='502', callback_data=("Ban" if second_try else "Stop")),
                              InlineKeyboardButton(text='25', callback_data=("Ban" if second_try else "Stop")),
                              InlineKeyboardButton(text='52', callback_data="Pass")]])],
        ['72:2', InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='34', callback_data=("Ban" if second_try else "Stop")),
                              InlineKeyboardButton(text='144', callback_data=("Ban" if second_try else "Stop")),
                              InlineKeyboardButton(text='36', callback_data="Pass"),
                              InlineKeyboardButton(text='70', callback_data=("Ban" if second_try else "Stop"))]])],
        ['29-5', InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='54', callback_data=("Ban" if second_try else "Stop")),
                              InlineKeyboardButton(text='290', callback_data=("Ban" if second_try else "Stop")),
                              InlineKeyboardButton(text='24', callback_data="Pass"),
                              InlineKeyboardButton(text='145', callback_data=("Ban" if second_try else "Stop"))]])],
        ['72:2', InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='34', callback_data=("Ban" if second_try else "Stop")),
                              InlineKeyboardButton(text='144', callback_data=("Ban" if second_try else "Stop")),
                              InlineKeyboardButton(text='36', callback_data="Pass"),
                              InlineKeyboardButton(text='70', callback_data=("Ban" if second_try else "Stop"))]])]
    ]

    rand = randint(0, len(captcha_variants) - 1)
    text = captcha_variants[rand][0]
    keyboard = captcha_variants[rand][1]
    return text, keyboard


def gen_menu_keyboard(menu_buttons=menu_buttons, admin: bool = False):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=menu_buttons[0], callback_data=f'{"set_text " if admin else ""}to_app')],
            [InlineKeyboardButton(text=menu_buttons[1], callback_data=f'{"set_text " if admin else ""}download')],
            [InlineKeyboardButton(text=menu_buttons[2], callback_data=f'{"set_text " if admin else ""}site')],
            [InlineKeyboardButton(text=menu_buttons[3], callback_data=f'{"set_text " if admin else ""}support')],
            [InlineKeyboardButton(text=menu_buttons[4], callback_data=f'{"set_text " if admin else ""}banks')]])


admin_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Редактирование сообщения бота', callback_data='change_message')],
                     [InlineKeyboardButton(text='Рассылка сообщения по пользователям', callback_data='spam')],
                     [InlineKeyboardButton(text='Заменить файл', callback_data='change_file')],
                     [InlineKeyboardButton(text='База пользователей', callback_data='database')]])
