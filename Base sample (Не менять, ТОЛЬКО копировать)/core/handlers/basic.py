from aiogram import Bot
from aiogram.types import Message


async def get_start(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, f'<b>привет, {message.from_user.first_name}. Рад тебя видеть!</b>')
    await message.answer(f'<s>привет, {message.from_user.first_name}. Рад тебя видеть!</s>')
    await message.reply(f'привет, {message.from_user.first_name}. Рад тебя видеть!')
