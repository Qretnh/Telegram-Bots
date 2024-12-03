import datetime
import time

import asyncpg
import asyncio


class database:
    async def connection(self):
        return await asyncpg.connect(user='postgres', password='qwaszx12', database='postgres',
                                     host='localhost', port=5432, command_timeout=10)

    async def check_table(self):
        con = await self.connection()
        async with con.transaction():
            await con.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER NOT NULL PRIMARY KEY,
            username TEXT,
            active TEXT DEFAULT 'NO',
            expires TEXT DEFAULT '2024-01-01');""")
        await con.close()

    async def add_user(self, id):
        con = await self.connection()
        async with con.transaction():
            await con.execute("""
                        INSERT INTO users (id)
                        VALUES ($1)
                        ON CONFLICT (id) DO NOTHING;
                        """, id)
        await con.close()

    async def update_user_subscription(self, id, months):
        date_expires = datetime.date.today() + datetime.timedelta(days=30 * months)
        con = await self.connection()
        async with con.transaction():
            await con.execute("""
                        UPDATE users 
                        SET expires = $2, active = $3 
                        WHERE id = $1;
                    """, id, str(date_expires), 'YES')
        await con.close()

    async def get_users_last_day(self):
        date = str(datetime.date.today())
        con = await self.connection()
        try:
            user_ids = await con.fetch("""
                        SELECT id FROM users
                        WHERE expires = $1 AND active = 'YES';
                        """, date)
            return [user.get("id") for user in user_ids]
        finally:
            await con.close()

    async def get_users_to_remove(self):
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        con = await self.connection()
        try:
            user_ids = await con.fetch("""
                        SELECT id FROM users
                        WHERE expires = $1 AND active = 'YES';
                        """, date)
            return [user.get("id") for user in user_ids]
        finally:
            await con.close()

    async def remove_user_subscription(self, id):
        con = await self.connection()
        async with con.transaction():
            await con.fetch("""
                            UPDATE users 
                            SET active = $1 
                            WHERE id = $2;
                            """, 'NO', id)
        await con.close()

    async def get_user_info(self, id):
        con = await self.connection()
        async with con.transaction():
            columns = await con.fetch("""
                                SELECT * FROM users
                                WHERE id = $1;
                                """, id)
            try:
                info = \
                    [[column.get("id"), column.get("username"), column.get("active"), column.get("expires")] for column
                     in
                     columns][0]
            except:
                info = []
        await con.close()
        return info

    async def get_all_users(self):
        con = await self.connection()
        async with con.transaction():
            columns = await con.fetch("""
                                        SELECT id FROM users;
                                        """)
            info = [column.get("id") for column in columns]
        await con.close()
        return info

DB = database()