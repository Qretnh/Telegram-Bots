from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.Price import Price as Price
from aiogram.filters.callback_data import CallbackData


class PriceCallbackFactory(CallbackData, prefix='PL'):
    category_id: int
    level1_name: int
    level2_name: int
    level3_name: int
    level4_name: int
    return_text: int


def generate_price_keyboard(callback: CallbackQuery = None, depth=0, width=2):
    kb_builder = InlineKeyboardBuilder()
    buttons = []

    if not callback:
        arr = Price.get_items()
        for i in range(len(arr)):
            buttons.append(
                InlineKeyboardButton(text=arr[i].name, callback_data=PriceCallbackFactory(category_id=i,
                                                                                          level1_name=-1,
                                                                                          level2_name=-1,
                                                                                          level3_name=-1,
                                                                                          level4_name=-1,
                                                                                          return_text=(-5 if type(arr[
                                                                                                                      i]) == str else 1)).pack()))
    else:
        # print(callback.data)
        article_info = [int(i) for i in callback.data[3:].split(':')]
        # print(article_info)
        if article_info[1] == -1:
            arr = Price.get_items()[article_info[0]].get_items()
            for i in range(len(arr)):
                buttons.append(
                    InlineKeyboardButton(text=(arr[i].name if type(arr[i]) != str else arr[i]),
                                         callback_data=PriceCallbackFactory(category_id=article_info[0],
                                                                            level1_name=i,
                                                                            level2_name=-1,
                                                                            level3_name=-1,
                                                                            level4_name=-1,
                                                                            return_text=(-5 if type(
                                                                                arr[i]) == str else 1)).pack()))
        elif article_info[2] == -1:
            arr = Price.get_items()[article_info[0]].get_items()[article_info[1]].get_items()
            for i in range(len(arr)):
                buttons.append(
                    InlineKeyboardButton(text=(arr[i].name if type(arr[i]) != str else arr[i]),
                                         callback_data=PriceCallbackFactory(category_id=article_info[0],
                                                                            level1_name=article_info[1],
                                                                            level2_name=i,
                                                                            level3_name=-1,
                                                                            level4_name=-1,
                                                                            return_text=(-5 if type(
                                                                                arr[i]) == str else 1)).pack()))
        elif article_info[3] == -1:
            arr = Price.get_items()[article_info[0]].get_items()[article_info[1]].get_items()[
                article_info[2]].get_items()
            for i in range(len(arr)):
                buttons.append(
                    InlineKeyboardButton(text=(arr[i].name if type(arr[i]) != str else arr[i]),
                                         callback_data=PriceCallbackFactory(category_id=article_info[0],
                                                                            level1_name=article_info[1],
                                                                            level2_name=article_info[2],
                                                                            level3_name=i,
                                                                            level4_name=-1,
                                                                            return_text=(-5 if type(
                                                                                arr[i]) == str else 1)).pack()))
        elif article_info[4] == -1:
            arr = \
                Price.get_items()[article_info[0]].get_items()[article_info[1]].get_items()[
                    article_info[2]].get_items()[
                    article_info[3]].get_items()
            for i in range(len(arr)):
                buttons.append(
                    InlineKeyboardButton(text=(arr[i].name if type(arr[i]) != str else arr[i]),
                                         callback_data=PriceCallbackFactory(category_id=article_info[0],
                                                                            level1_name=article_info[1],
                                                                            level2_name=article_info[2],
                                                                            level3_name=article_info[3],
                                                                            level4_name=i,
                                                                            return_text=0).pack()))

    kb_builder.row(*buttons, width=2)
    kb = kb_builder.as_markup()

    if callback:
        if article_info[1] == -1:
            kb.inline_keyboard.append([InlineKeyboardButton(text='Назад', callback_data='back_to_price')])
        else:
            i = 1
            while article_info[i] != -1:
                i += 1
            article_info[i - 1] = -1
            callback_to_prev_button = 'PL:' + ''.join([str(i) + ':' for i in article_info])
            kb.inline_keyboard.append([InlineKeyboardButton(text='Назад', callback_data=callback_to_prev_button[:-1])])

    return kb


def send_number_keyboard():
    kb_builder = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Поделиться контактом',
                                                               request_contact=True)]],
                                     resize_keyboard=True,
                                     one_time_keyboard=True)
    return kb_builder
