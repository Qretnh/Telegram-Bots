import datetime
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent

from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, Multi, List, Case
from aiogram_dialog.widgets.kbd import SwitchTo

from environs import Env

from app.bot.database.db_funcs import get_catalog, get_subcategories, get_products, get_current_product, \
    get_all_products, \
    update_order, add_to_users
from app.bot.payments.youkassa import order
from app.bot.services.FAQ import FAQ

from ..services.utils import save_order_and_update_excel

router = Router()

env = Env()
env.read_env()


class FSM(StatesGroup):
    question = State()
    to_payment = State()
    product_window = State()
    start = State()
    cart = State()
    catalog = State()
    FAQ = State()
    categories = State()
    subcategories = State()
    products = State()
    approve_product = State()
    count = State()


def check_digit(text: str):
    return int(text)


async def to_subcategory(callback: CallbackQuery,
                         widget: Select,
                         dialog_manager: DialogManager,
                         item_id: str):
    dialog_manager.dialog_data.update({"category": item_id})
    await dialog_manager.switch_to(FSM.subcategories)


async def pass_func(message: Message,
                    widget: ManagedTextInput,
                    dialog_manager: DialogManager,
                    text: str):
    dialog_manager.show_mode = ShowMode.NO_UPDATE


async def move_to_cart(message: Message,
                       widget: ManagedTextInput,
                       dialog_manager: DialogManager,
                       text: str):
    session = dialog_manager.middleware_data['session']
    category = dialog_manager.dialog_data["category"]
    subcategory = dialog_manager.dialog_data["subcategory"]
    product = dialog_manager.dialog_data["product"]
    product = await get_current_product(session, category, subcategory, product)

    try:
        cart = dialog_manager.dialog_data['cart']
    except Exception as e:
        cart = []

    cart.append({'product_id': product[4],
                 'amount': int(text)})
    dialog_manager.dialog_data.update({'cart': cart})
    await dialog_manager.switch_to(FSM.approve_product)


async def to_products(callback: CallbackQuery,
                      widget: Select,
                      dialog_manager: DialogManager,
                      item_id: str):
    dialog_manager.dialog_data.update({"subcategory": item_id})
    await dialog_manager.switch_to(FSM.products)


async def to_product_window(callback: CallbackQuery,
                            widget: Select,
                            dialog_manager: DialogManager,
                            item_id: str):
    dialog_manager.dialog_data.update({"product": item_id})
    await dialog_manager.switch_to(FSM.product_window)


async def clear_cart(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):
    dialog_manager.dialog_data['cart'] = []


async def show_answer(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager,
                      text: str):
    FAQ_list = list(FAQ.keys())
    question_num = FAQ_list.index(text)
    dialog_manager.dialog_data['question_num'] = question_num
    await dialog_manager.switch_to(FSM.question)


async def back_and_switch_show_mode(callback: CallbackQuery,
                                    button: Button,
                                    dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.switch_to(FSM.start)


async def payment(callback: CallbackQuery,
                  button: Button,
                  dialog_manager: DialogManager, **kwargs):
    items = dialog_manager.dialog_data['items_in_cart']

    order_products = ''
    for item in items:
        order_products += item[0] + "_" + str(item[1]) + "шт._" + str(item[2]) + "руб.\n"

    total_cost = dialog_manager.dialog_data['total_cost']
    await order(callback.from_user.id, callback.bot, products=order_products, total_price=total_cost)


async def add_to_cart(callback: CallbackQuery,
                      widget: Select,
                      dialog_manager: DialogManager,
                      item_id: str):
    dialog_manager.dialog_data.update({"product": item_id})
    await dialog_manager.switch_to(FSM.product_window)


async def getter_subcategories(dialog_manager: DialogManager,
                               dispatcher: Dispatcher,
                               **kwargs):
    session = dialog_manager.middleware_data['session']
    category = dialog_manager.dialog_data["category"]
    subcategories = await get_subcategories(session, category)
    return {'subcategories': subcategories}


async def getter_categories(dialog_manager: DialogManager,
                            dispatcher: Dispatcher,
                            **kwargs):
    session = dialog_manager.middleware_data['session']
    category = dialog_manager.dialog_data["category"]
    subcategories = await get_subcategories(session, category)
    return {'subcategories': subcategories}


async def getter_catalog(dialog_manager: DialogManager,
                         dispatcher: Dispatcher,
                         **kwargs):
    session = dialog_manager.middleware_data['session']
    catalog = await get_catalog(session)
    return {'catalog': catalog}


async def getter_products(dialog_manager: DialogManager,
                          dispatcher: Dispatcher,
                          **kwargs):
    session = dialog_manager.middleware_data['session']
    category = dialog_manager.dialog_data["category"]
    subcategory = dialog_manager.dialog_data["subcategory"]
    products = await get_products(session, category, subcategory)

    return {'products': products,
            'subcategory': subcategory}


async def getter_cart(dialog_manager: DialogManager,
                      dispatcher: Dispatcher,
                      **kwargs):
    session = dialog_manager.middleware_data['session']
    products = await get_all_products(session)

    try:
        cart = dialog_manager.dialog_data['cart']
    except Exception as e:
        cart = []
    items_in_cart = []

    total_cost = 0
    for item in cart:
        product = [product for product in products if product[4] == item['product_id']][0]
        items_in_cart.append((product[0], item['amount'], product[1], item['amount'] * product[1]))
        total_cost += item['amount'] * product[1]

    dialog_manager.dialog_data['total_cost'] = total_cost
    dialog_manager.dialog_data['items_in_cart'] = items_in_cart

    return {'total_cost': total_cost,
            'items_in_cart': items_in_cart,
            'cart_is_not_empty': len(cart) > 0}


async def getter_question(dialog_manager: DialogManager,
                          dispatcher: Dispatcher,
                          **kwargs):
    question = list(FAQ.items())[dialog_manager.dialog_data['question_num']]
    return {'question': question[0],
            'answer': question[1]}


async def getter_current_product(dialog_manager: DialogManager,
                                 dispatcher: Dispatcher,
                                 **kwargs):
    session = dialog_manager.middleware_data['session']
    category = dialog_manager.dialog_data["category"]
    subcategory = dialog_manager.dialog_data["subcategory"]
    product = dialog_manager.dialog_data["product"]
    product = await get_current_product(session, category, subcategory, product)

    return {'name': product[0],
            'price': product[1],
            'description': product[2],
            'photo': MediaAttachment(type=ContentType.PHOTO,
                                     path=os.path.join("/app", "app", "bot", "photos", category, subcategory,
                                                       product[3])),
            'subcategory': subcategory}


async def getter_FAQ(dialog_manager: DialogManager,
                     dispatcher: Dispatcher,
                     **kwargs):
    return {"questions": FAQ.keys()}


dialog = Dialog(
    Window(
        Const("Добро пожаловать в <s>импровизированный</s> магазин по продаже электроники!\n\n"
              "<b>🛒 Каталог</b> - Для поиска и выбора по ассортименту товаров. Просто выберите нужную категорию\n\n"
              "<b>🛍 Корзина</b> - Для просмотра выбранных товаров и оформления заказа\n\n"
              "<b>❓ F.A.Q.</b> - Для поиска ответов на часто задаваемые вопросы нажмите "),
        SwitchTo(Const("🛒 Каталог"),
                 id="catalog",
                 state=FSM.catalog),
        SwitchTo(Const("🛍 Корзина"),
                 id="cart",
                 state=FSM.cart),
        SwitchTo(Const("❓ F.A.Q."),
                 id="FAQ",
                 state=FSM.FAQ),
        state=FSM.start
    ),
    Window(
        Const("Категории товаров"),
        ScrollingGroup(
            Select(Format("{item}"),
                   id="catalog_buttons",
                   item_id_getter=lambda x: str(x),
                   items="catalog",
                   on_click=to_subcategory),
            height=4,
            width=1,
            id="catalog_group"),
        SwitchTo(Const("◀️ Назад"),
                 id='back_to_start',
                 state=FSM.start),
        getter=getter_catalog,
        state=FSM.catalog
    ),
    Window(
        Const("Выберите подкатегорию"),
        ScrollingGroup(
            Select(Format("{item}"),
                   id="subcategories_buttons",
                   item_id_getter=lambda x: str(x),
                   items="subcategories",
                   on_click=to_products),
            height=5,
            width=2,
            id="subcategories_group"),
        SwitchTo(Const("◀️ Назад"),
                 id='back_to_catalog',
                 state=FSM.catalog),
        getter=getter_categories,
        state=FSM.subcategories
    ),
    Window(
        Format("{subcategory}"),
        ScrollingGroup(
            Select(Format("{item}"),
                   id="products_buttons",
                   item_id_getter=lambda x: str(x),
                   items="products",
                   on_click=to_product_window),
            height=5,
            width=2,
            id="products_group"),
        SwitchTo(Const("◀️ Назад"),
                 id='back_to_subcategories',
                 state=FSM.subcategories),
        getter=getter_products,
        state=FSM.products
    ),
    Window(Format("<i>{dialog_data[category]} / {dialog_data[subcategory]}</i>\n\n"
                  "{name}\n\n"
                  "Цена: {price} руб.\n\n"
                  "Описание: {description}"),
           DynamicMedia('photo'),
           SwitchTo(Const("🛒 Добавить в корзину"),
                    id='add_to_cart',
                    state=FSM.count),
           SwitchTo(Const("◀️ Назад"),
                    id='back_to_products',
                    state=FSM.products),
           getter=getter_current_product,
           state=FSM.product_window
           ),
    Window(Format("Введите желаемое количество единиц товара (в ответном сообщении одно число, без лишних пробелов)\n\n"
                  "<i>После ввода товар будет добавлен в вашу корзину</i>"),
           TextInput(id='input_count',
                     type_factory=check_digit,
                     on_success=move_to_cart),
           SwitchTo(Const("↩️ Обратно в каталог"),
                    id="back_to_product",
                    state=FSM.product_window),
           state=FSM.count),
    Window(Format("✅ Товар успешно добавлен в корзину!\n"
                  "Можете продолжить выбор товаров в каталоге или перейти в корзину, чтобы завершить покупку"),
           SwitchTo(Const("🛒 Перейти в корзину"),
                    id="to_cart",
                    state=FSM.cart),
           SwitchTo(Const("↩️ Обратно в каталог"),
                    id="back_to_catalog",
                    state=FSM.catalog),
           state=FSM.approve_product),
    Window(Const("🛒 Корзина\n"),
           Case(texts={
               0: Const("Ваша корзина сейчас пуста"),
               1: Multi(
                   List(
                       Format("{item[0]}\n"
                              "{item[1]}шт. x {item[2]} руб.\n"
                              "{item[3]} руб."),
                       sep='\n\n',
                       items='items_in_cart'),
                   Format("___________\n\n"
                          "<b>Итого: {total_cost} рублей.</b>")
               )
           },
               selector="cart_is_not_empty"),
           SwitchTo(Const("🛍 Перейти в каталог"),
                    id="switch_to_catalog",
                    state=FSM.catalog),
           Button(Const("✅ Перейти к оформлению"),
                  id="to_payment",
                  on_click=payment,
                  when="cart_is_not_empty"),
           Button(Const("🧹 Очистить корзину"),
                  id="clear_cart",
                  on_click=clear_cart),
           SwitchTo(Const("◀️ Назад"),
                    id='back_to_start_from_cart',
                    state=FSM.start),
           getter=getter_cart,
           state=FSM.cart
           ),
    Window(
        Const("❓ Ответы на часто задаваемые вопросы\n\n"
              "Для поиска ответа на интересующие вас вопросы, воспользуйтесть inline-режимом: Укажите имя бота в поле"
              "для ввода сообщений и начните вводите интересующий вас вопрос (пример на фото), бот подскажет, "
              "что вам может пригодиться😉\n\n"
              "Так же вопросы продублированы в списке ниже."),
        ScrollingGroup(
            Select(
                Format("{item}"),
                id='faq',
                item_id_getter=lambda x: str(x),
                items="questions",
                on_click=show_answer
            ),
            width=1,
            height=6,
            id='faq_buttons_group'
        ),
        Button(Const("◀️ Назад"),
               id='back_and_switch_show_mode',
               on_click=back_and_switch_show_mode),
        TextInput(id="input",
                  type_factory=lambda x: Exception,
                  on_success=pass_func),
        getter=getter_FAQ,
        state=FSM.FAQ
    ),
    Window(
        Format("❓ {question}\n\n"
               "▶️ {answer}"),
        SwitchTo(Const("◀️ Назад"),
                 id='back_to_products',
                 state=FSM.FAQ),
        state=FSM.question,
        getter=getter_question
    )
)


@router.message(Command(commands=['start']))
async def command_start(message: Message, dialog_manager: DialogManager,
                        **kwargs):
    session = kwargs['session']
    await add_to_users(session, message.from_user.id)  # добавление пользователя в бд
    await dialog_manager.start(state=FSM.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.DELETE_AND_SEND)


@router.pre_checkout_query()
async def shipping_check(pre_checkout_query: PreCheckoutQuery,
                         bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message="Ошибка")  # всегда отвечаем утвердительно


@router.message(F.successful_payment)
async def process_successful_payment(message: Message,
                                     **kwargs):
    await message.answer("Оплата успешно прошла!")

    # получение аргументов
    session = kwargs['session']
    price = message.successful_payment.total_amount // 100
    email = message.successful_payment.order_info.email
    address_info = message.successful_payment.order_info.shipping_address
    address = address_info.state + " " + address_info.city + " " + address_info.street_line1 + " " + address_info.street_line2 + " " + address_info.post_code
    phone_number = int(message.successful_payment.order_info.phone_number)
    info = message.successful_payment.invoice_payload.replace('\n', ' & ')
    time = str(datetime.datetime.now().replace(microsecond=0))

    # добавление заказа в бд
    await update_order(session, info, price, phone_number, email, address, time)

    # создание новой записи в excel-таблице
    save_order_and_update_excel(items=info, price=price, phone_number=phone_number, email=email, address=address,
                                complete=0)


@router.inline_query()
async def faq_answers(query: InlineQuery):
    faq_data = FAQ
    # Получаем текст запроса
    query_text = query.query.lower()

    # Фильтруем вопросы по запросу
    results = []
    for question, answer in faq_data.items():
        if query_text in question.lower():
            results.append(
                InlineQueryResultArticle(
                    id=question,
                    title=question,
                    input_message_content=InputTextMessageContent(message_text=answer)
                )
            )

    # Отправляем результаты
    await query.answer(results, cache_time=5)
