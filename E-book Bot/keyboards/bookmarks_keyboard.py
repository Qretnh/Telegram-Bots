from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def bookmarks_list_keyboard(bookmarks_list):
    buttons = []
    CancelButton = InlineKeyboardButton(text='Отменить', callback_data='cancel')
    RemoveButton = InlineKeyboardButton(text='Редактировать✖️', callback_data='edit_bookmarks')
    for page, desc in bookmarks_list:
        buttons.append([InlineKeyboardButton(text=f'{page} | {desc}', callback_data=f'page {page}')])
    buttons.append([RemoveButton, CancelButton])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_bookmarks_list_keyboard(bookmarks_list):
    CancelButton = InlineKeyboardButton(text='Отменить', callback_data='cancel')
    BackToBookmarksButton = InlineKeyboardButton(text='Отменить редактирование', callback_data='bookmarks')
    buttons = []

    for page, desc in bookmarks_list:
        buttons.append([InlineKeyboardButton(text=f'❌ {page} | {desc}', callback_data=f'delete_page {page}')])
    buttons.append([BackToBookmarksButton, CancelButton])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
