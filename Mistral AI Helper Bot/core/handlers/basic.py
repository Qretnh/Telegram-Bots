import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import core.handlers.ai_functions as ai_functions
import json


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Я - виртуальный помощник на базе ИИ Mistral. напиши свой запрос, я на него отвечу')


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(
        'Я - виртуальный помощник на базе ИИ Mistral. напиши свой запрос, я на него отвечу'
    )


# Этот хэндлер будет очищать контекст сообщений для конкретного пользователя"
@dp.message(Command(commands=['clear']))
async def process_help_command(message: Message):
    user_id = str(json.loads(str(message.json()))['from_user']['id'])
    context.pop(user_id)


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"
@dp.message()
async def send_echo(message: Message):
    thinking_message = await message.answer(
        'Думаю над ответом... '
    )

    user_id = str(json.loads(str(message.json()))['from_user']['id'])

    try:
        if user_id not in context.keys():
            answer = ai_functions.get_llm_mesage(message.text)
        else:
            answer = ai_functions.get_llm_mesage(message.text, context=context[user_id])

        await message.reply(text=answer)

        if user_id in context:
            context[user_id].append(message.text)
            context[user_id].append(ai_functions.get_llm_mesage(message.text))
        else:
            context[user_id] = [message.text, answer]

    except Exception:
        await message.reply(text='Произошла непредвиденная ошибка, попробуйте ещё раз')

    await thinking_message.delete()

