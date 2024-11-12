from typing import List, Tuple, Any

import asyncpg

from asyncpg import Record


class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_data(self, user_id, text, message_id):
        query = f"INSERT INTO appeals (unique_id, user_id, status, text) VALUES ('{message_id}', {user_id}, 'New', '{text}')"
        await self.connector.execute(query)

    async def fetch_appeals_count(self, table_name='appeals'):
        query = f"SELECT * FROM {table_name} WHERE status = 'New'"
        answer = await self.connector.fetch(query)
        count = len(answer)
        return count

    async def fetch_appeals(self, table_name='appeals'):
        query = f"SELECT * FROM {table_name} WHERE status = 'New'"
        answer = await self.connector.fetch(query)
        answer = [list(record.values()) for record in answer]
        return answer

    async def set_answer(self, unique_id):
        query = f"UPDATE appeals SET status = 'Answered' WHERE unique_id = '{unique_id}';"
        await self.connector.execute(query)

    async def check_banned(self, user_id):
        query = f"SELECT * FROM bot_users WHERE status = 'Banned'"
        response = await self.connector.fetch(query)
        banned_users = [list(record.values()) for record in response]

        for record in banned_users:
            if record[0] == user_id:
                return 1
        return 0

    async def ban_user(self, user_id):
        query = f"UPDATE bot_users SET status = 'Banned' WHERE user_id = {user_id};"
        await self.connector.execute(query)

    async def unban_user(self, user_id):
        query = f"UPDATE bot_users SET status = 'Active' WHERE user_id = {user_id};"
        await self.connector.execute(query)
