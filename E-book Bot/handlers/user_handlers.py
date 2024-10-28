from aiogram import Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from keyboards.keyboard import base_pagination_keyboard
from keyboards.bookmarks_keyboard import bookmarks_list_keyboard, edit_bookmarks_list_keyboard
from books.books_logic import Book_shelf

from services.logic import (add_new_user, read_next_page, read_prev_page, set_user_bookmark, get_user_book,
                            get_reading_info, remove_bookmark_from_user,
                            get_bookmarks)

# from lexicon.lexicon import LEXICON_RU
# from keyboards.keyboards import offer_keyboard, choose_keyboard, wait_keyboard
# from services.game_logic import move, stats, update_stats

from aiogram.types import callback_query

router = Router()


@router.message(Command(commands=['start']))
async def command_start(message: Message):
    await message.answer(text='Привет, я бот-читалка. Сейчас вы можете начать читать книгу Д. Грэй "Мужчины с марса, '
                              'женщины с венеры"\n\nДля более подробной информации воспользуйтесь командой '
                              '/help\n\nЧтобы начать читать, введите /begin')


@router.message(Command(commands=['begin']))
async def command_start(message: Message):
    add_new_user(message.from_user.id)
    book = get_user_book(message.from_user.id)
    await message.answer(text='Загружаю книгу...')
    await message.answer(text=book.get_page(1),
                         reply_markup=base_pagination_keyboard(1, book.length, is_pinned=False))


@router.message(Command(commands=['help']))
async def help(message: Message):
    await message.answer(text='Основная информация по команднам:\n\n'
                              '/help - Основная информация по командам бота\n'
                              '/begin - Начать чтение с 1 страницы\n'
                              '/continue - Продолжить чтение с последней страницы\n'
                              '/bookmarks - Закладки пользователя. Добавить её можно нажав на номер страницы во время '
                              'чтения, а открыть или изменить существующие закладки, внутри данной команды'
                              '\n\nПриятного пользования!')


@router.message(Command(commands=['bookmarks']))
async def show_bookmarks(message: Message):
    id = message.from_user.id
    bookmarks = get_bookmarks(id)
    if bookmarks and len(bookmarks) > 0:
        await message.answer(
            text='Добро пожаловать в закладки. Здесь вы можете перейти к своим закладкам через список ниже.',
            reply_markup=bookmarks_list_keyboard(bookmarks))
    else:
        await message.answer(text='В данный момент у вас нет закладок.\n'
                                  'Вы можете продолжить чтение командой /continue')


@router.message(Command(commands=['continue']))
async def continue_reading(message: Message):
    id = message.from_user.id
    num, book, page, is_pinned = get_reading_info(id)
    await message.answer(text=page,
                         reply_markup=base_pagination_keyboard(num, book.length, is_pinned))


@router.callback_query(F.data == 'bookmarks')
async def show_bookmarks_callback(callback: CallbackQuery):
    id = callback.from_user.id
    await callback.message.edit_text(
        text='Добро пожаловать в закладки. Здесь вы можете перейти к своим закладкам через список ниже.',
        reply_markup=bookmarks_list_keyboard(get_bookmarks(id)))


@router.callback_query(F.data == 'edit_bookmarks')
async def edit_bookmarks(callback: CallbackQuery):
    id = callback.from_user.id
    await callback.message.edit_text(
        text='Чтобы удалить закладку, нажмите на неё. Вернуться к переходу можно через кнопку "Отмена"',
        reply_markup=edit_bookmarks_list_keyboard(get_bookmarks(id)))


@router.callback_query(F.data == 'next_page')
async def get_next_page(callback: CallbackQuery):
    id = callback.from_user.id
    num, book, page, is_pinned = read_next_page(id)
    await callback.message.edit_text(text=page,
                                     reply_markup=base_pagination_keyboard(num, book.length, is_pinned))


@router.callback_query(F.data == 'prev_page')
async def get_next_page(callback: CallbackQuery):
    id = callback.from_user.id
    num, book, page, is_pinned = read_prev_page(id)
    await callback.message.edit_text(text=page,
                                     reply_markup=base_pagination_keyboard(num, book.length, is_pinned))


@router.callback_query(F.data == 'set_bookmark')
async def set_bookmark(callback: CallbackQuery):
    id = callback.from_user.id
    answer = set_user_bookmark(id)
    num, book, page, is_pinned = get_reading_info(id)
    await callback.answer(text=answer)
    await callback.message.edit_reply_markup(reply_markup=base_pagination_keyboard(num, book.length, is_pinned))


@router.callback_query(F.data == 'cancel')
async def set_bookmark(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text='Продолжить чтение можно командой /continue')


@router.callback_query(F.data.startswith('page'))
async def move_to_page(callback: CallbackQuery):
    id = callback.from_user.id
    called_page = int(callback.data[5:])
    num, book, page, is_pinned = read_next_page(id, new_page=called_page)
    await callback.message.edit_text(text=page,
                                     reply_markup=base_pagination_keyboard(num, book.length, is_pinned))


@router.callback_query(F.data.startswith('delete_page'))
async def remove_bookmark(callback: CallbackQuery):
    id = callback.from_user.id
    page_to_remove = int(callback.data[11:])
    if not remove_bookmark_from_user(id, page_to_remove):
        await callback.message.edit_reply_markup(reply_markup=edit_bookmarks_list_keyboard(get_bookmarks(id)))
    else:
        await callback.message.delete()
        await callback.message.answer(text='Продолжить чтение можно командой /continue')