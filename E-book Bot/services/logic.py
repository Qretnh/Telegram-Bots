import database.users as users
import books.books_logic as books_logic
from books.books_logic import Book_shelf


def get_user_book(id: int):
    return Book_shelf[users.users_info[id]['book']]


def is_pinned_page(id: int, page: int):
    return page in users.users_info[id]['bookmarks']


def add_new_user(id: int):
    if id not in users.users_info.keys():
        users.users_info[id] = {'book': 'Men_From_Mars',
                                'page': 1,
                                'bookmarks': []}
        print(users.users_info)


def get_reading_info(id: int):
    is_pinned = False
    try:
        page = users.users_info[id]['page']
    except KeyError:
        add_new_user(id)
    page = users.users_info[id]['page']

    if is_pinned_page(id, page):
        is_pinned = True

    book = get_user_book(id)

    return [page,
            book,
            book.get_page(page),
            is_pinned]


def read_next_page(id: int, new_page: int = 0):
    is_pinned = False

    if new_page > 0:
        users.users_info[id]['page'] = new_page
    else:
        users.users_info[id]['page'] += 1
    page = users.users_info[id]['page']

    if is_pinned_page(id, page):
        is_pinned = True

    book = get_user_book(id)

    return [page,
            book,
            book.get_page(page),
            is_pinned]


def read_prev_page(id: int):
    is_pinned = False

    users.users_info[id]['page'] -= 1
    page = users.users_info[id]['page']

    if is_pinned_page(id, page):
        is_pinned = True

    book = get_user_book(id)

    return [page,
            book,
            book.get_page(page),
            is_pinned]


def set_user_bookmark(id: int) -> str:
    page = users.users_info[id]['page']

    if page in users.users_info[id]['bookmarks']:
        users.users_info[id]['bookmarks'].remove(page)
        answer = 'Страница убрана из закладок. Просмотреть заметки вы можете набрав команду /bookmarks'
    else:
        users.users_info[id]['bookmarks'].append(page)
        answer = 'Страница успешно добавлена в закладки. Можете найти её набрав команду /bookmarks'
    return answer


def get_bookmarks(id: int):
    try:
        bookmarks = users.users_info[id]['bookmarks']
    except KeyError:
        return None

    book = get_user_book(id)
    bookmarks_list = [[int(page), book.get_page(page)[0:100] + '...'] for page in bookmarks]
    return bookmarks_list


def remove_bookmark_from_user(id: int, page: int):
    users.users_info[id]['bookmarks'].remove(page)
    if len(users.users_info[id]['bookmarks']) == 0:
        return 1
