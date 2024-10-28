from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

start_pagination_keyboard = InlineKeyboardMarkup


def base_pagination_keyboard(page: int, all_pages: int, is_pinned: bool):
    if is_pinned:
        pin = '🔖'
    else:
        pin = ''

    PrevPageButton = InlineKeyboardButton(text='<<<', callback_data='prev_page')
    PageButton = InlineKeyboardButton(text=f'{page}/{all_pages}{pin}', callback_data='set_bookmark')
    NextPageButton = InlineKeyboardButton(text='>>>', callback_data='next_page')

    if page == 1:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[PageButton, NextPageButton]])

    elif page < all_pages:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[PrevPageButton, PageButton, NextPageButton]])
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[PrevPageButton, PageButton]])
    return keyboard
