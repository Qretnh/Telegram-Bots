from pyrogram import Client, idle, filters
from pyrogram.types import Message
from datetime import datetime as DT
from pyrogram.handlers import MessageHandler
from Neuro import get_neuro_comment
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


target_channel = os.getenv("TARGET")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
client = Client('new_session', API_ID, API_HASH)


async def handler(client: Client, message: Message):
    last_message = await client.get_discussion_message(target_channel, message.id)
    comment_to_post = await get_neuro_comment(last_message.text.replace("\n", " "))
    await last_message.reply(comment_to_post)


client.add_handler(MessageHandler(handler, filters.chat(target_channel)))
client.start()
idle()
