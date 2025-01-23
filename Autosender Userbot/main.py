import asyncio
import os

from pyrogram import Client

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

subscribed_channels = []
channels_to_post = []

with open('channels_from_id.txt', 'r') as file:
    subscribed_channels.append(file.readline())

with open('channels_to_id.txt', 'r') as file:
    channels_to_post.append(file.readline())

print(subscribed_channels)
# ID канала, куда будем выкладывать посты


app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH)

# Множество для хранения ID уже пересланных сообщений
sent_messages = set()


async def main():
    async with app:
        while True:
            messages_sent_this_pass = set()  # Множество для отслеживания отправленных сообщений в текущем проходе

            for channel_id in subscribed_channels:
                try:
                    # Получаем последние сообщения из канала
                    async for message in app.get_chat_history(channel_id, limit=5):  # Измените limit по необходимости
                        if message and (message.message_id not in sent_messages):  # Проверяем, что сообщение текстовое и его еще не отправляли

                            for channel in channels_to_post:
                                await app.send_message(channel, message)

                            sent_messages.add(message.message_id)  # Добавляем ID сообщения в множество
                            messages_sent_this_pass.add(
                                message.message_id)  # Добавляем в множество отправленных сообщений

                except Exception as e:
                    print(f"Ошибка при обработке канала {channel_id}: {e}")

            # Автоочистка sent_messages
            if len(messages_sent_this_pass) < len(subscribed_channels) * 5:  # Если не все сообщения были отправлены
                sent_messages.intersection_update(
                    messages_sent_this_pass)  # Оставляем только те сообщения, которые были отправлены в текущем проходе

            await asyncio.sleep(int(os.environ.get("DELAY")))  # Задержка перед следующей итерацией (например, 60 секунд)


if __name__ == "__main__":
    asyncio.run(main())
