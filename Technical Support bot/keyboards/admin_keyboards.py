from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=
[
    [
        InlineKeyboardButton(text='Входящие обращения',
                             callback_data='new_appeals')
    ],
    [
        InlineKeyboardButton(text='Управление пользователями',
                             callback_data='users_admin')
    ]
])

admin_ban_unban_keyboard = InlineKeyboardMarkup(inline_keyboard=
[
    [
        InlineKeyboardButton(text='Забанить пользователя',
                             callback_data='admin_ban')
    ],
    [
        InlineKeyboardButton(text='Разбанить пользователя',
                             callback_data='admin_unban')
    ]
])
