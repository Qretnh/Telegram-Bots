import asyncio
import time

import aiosqlite
from sqlalchemy import insert, select, update, delete
from datetime import datetime, timedelta
from sqlalchemy import ForeignKey, Date, DATE, DateTime, DATETIME
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker, async_session
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.schema import CreateTable
from database.db import User, Master, Record, Service, BasicInfo, WorkShift, Admin, Ban


async def get_user(
        session: AsyncSession,
        id: int,
        username: str,
):
    stmt = select(User).where(User.user_id == id)
    result = await session.execute(stmt)
    user_info = result.scalars().all()
    return user_info


async def add_user(
        session: AsyncSession,
        id: int,
        username: str,
        birthdate: str,
        tg_username: str,
        phone_number: int
):
    user = User(user_id=id,
                username=username,
                phone_number=phone_number,
                tg_username=tg_username)
    session.add(user)
    await session.commit()

async def append_master(session: AsyncSession, username):
    stmt = select(User).where(User.user_id==username)
    result = await session.execute(stmt)
    result = result.scalars().first()
    master_id = result[0].user_id
    stmt = insert(Master)

async def is_master(
        session: AsyncSession,
        id: int,
        username: str,
):
    stmt = select(Master).where(Master.user_id == id)
    result = await session.execute(stmt)
    trainings = result.scalars().all()
    return trainings


async def base_init(sessionmaker):
    async with sessionmaker() as session:
        config = BasicInfo(start_hour=9,
                           last_hour=22,
                           timezone=0)
        session.add(config)
        await session.commit()


async def get_admins(session: AsyncSession):
    stmt = select(Admin)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_banned_users(session: AsyncSession):
    stmt = select(Ban)
    result = await session.execute(stmt)
    result = result.scalars().all()
    print(result)
    result = [item.user_id for item in result]
    return result


async def get_masters(session: AsyncSession):
    stmt = select(Master)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_master_services(master_id: int, session: AsyncSession):
    stmt = select(Service).where(Master.user_id == master_id)
    result = await session.execute(stmt)
    result = result.scalars().all()
    return result


async def get_user_records(user_id, session: AsyncSession):
    stmt = select(Record).where(Record.date >= datetime.today().date())
    result = await session.execute(stmt)
    result = result.scalars().all()
    records = [
        [record.name, record.time, record.length, await get_master_name(master_id=record.master, session=session),
         record.date] for record in result]
    return records


async def get_master_records_date(user_id, date, session):
    stmt = select(Record).where(Record.master == user_id, Record.date == date)
    result = await session.execute(stmt)
    result = result.scalars().all()
    records = [[record.name, record.date, record.time] for record in result]
    return records


async def get_master_records_today(user_id, session):
    stmt = select(Record).where(Record.master == user_id, Record.date == datetime.today().date())
    result = await session.execute(stmt)
    result = result.scalars().all()
    records = [[record.name, record.date, record.time] for record in result]
    records = sorted(records, key=lambda x: datetime.strptime(x[2], '%H:%M'))
    print('records', records)
    return records


async def get_master_name(master_id: int, session: AsyncSession):
    stmt = select(Master).where(Master.user_id == master_id)
    result = await session.execute(stmt)
    result = result.scalars().all()
    result = result[0].name
    return result


async def insert_service(master_id: int, session: AsyncSession, title: str, length: int, description: str, price: int):
    stmt = insert(Service).values(user_id=master_id,
                                  name=title,
                                  length=length,
                                  description=description,
                                  price=price)
    await session.execute(stmt)
    await session.commit()


async def delete_service(unique_id: int, session: AsyncSession):
    stmt = delete(Service).where(Service.unique_id == unique_id)
    await session.execute(stmt)
    await session.commit()


async def update_name(master_id: int, new_name: str, session: AsyncSession):
    result = await session.execute(
        select(Master).where(Master.user_id == master_id)
    )
    user_to_update = result.scalars().first()
    user_to_update.name = new_name
    await session.commit()


async def update_photo(master_id: int, new_photo: str, session: AsyncSession):
    result = await session.execute(
        select(Master).where(Master.user_id == master_id)
    )
    user_to_update = result.scalars().first()
    user_to_update.photo = new_photo
    await session.commit()


async def update_description(master_id: int, new_description: str, session: AsyncSession):
    result = await session.execute(
        select(Master).where(Master.user_id == master_id)
    )
    user_to_update = result.scalars().first()
    user_to_update.description = new_description
    await session.commit()


async def get_shift(master_id: int, date, session):
    stmt = select(WorkShift).where(WorkShift.master_id == master_id, WorkShift.date == date)
    result = await session.execute(stmt)
    shifts = result.scalars().all()  # Получаем все записи

    return len(shifts)  # Возвращаем количество смен


async def get_shifts(master_id: int, session: AsyncSession):
    stmt = select(WorkShift).where(WorkShift.master_id == master_id, WorkShift.date >= datetime.today().date())

    result = await session.execute(stmt)
    shifts = result.scalars().all()
    shifts = [[shift.date, shift.start_time, shift.end_time, master_id] for shift in shifts]
    return shifts


async def get_shifts_today(master_id: int, session: AsyncSession):
    stmt = select(WorkShift).where(WorkShift.master_id == master_id, WorkShift.date == datetime.today().date())
    result = await session.execute(stmt)
    shifts = result.scalars().all()
    shifts = [[shift.date, shift.start_time, shift.end_time, master_id] for shift in shifts]
    return shifts


async def delete_shift(master_id: int, date, session):
    stmt = delete(WorkShift).where(WorkShift.master_id == master_id, WorkShift.date == date)
    await session.execute(stmt)
    await session.commit()


async def set_shift(master_id: int, date, start_hour: int, end_hour: int, session):
    stmt = insert(WorkShift).values(master_id=master_id, date=date, start_time=start_hour, end_time=end_hour)
    await session.execute(stmt)
    await session.commit()


async def check_records(master_id: int, date, session):
    date = datetime.strptime(date, '%d-%m-%Y').date()
    stmt = select(Record).where(Record.master == master_id, Record.date == date)
    result = await session.execute(stmt)
    records = [[record.time,
                (datetime.combine(datetime.today(), datetime.strptime(record.time, '%H:%M').time()) + timedelta(
                    minutes=record.length)).strftime("%H:%M")]
               for record in result.scalars().all()]
    return records


async def add_record(master_id, selected_date, selected_time, length, price, client_id, name, session):
    date = datetime.strptime(selected_date, '%d-%m-%Y').date()
    if selected_time.count(':') == 2:
        time_obj = time.strptime(selected_time, "%H:%M:%S")

        formatted_time = f"{time_obj.tm_hour}:{time_obj.tm_min:02}"
    else:
        formatted_time = selected_time
    print('add_record time', selected_time)
    stmt = insert(Record).values(master=master_id, date=date, time=formatted_time,
                                 name=name, length=length, price=price,
                                 client_id=client_id)
    await session.execute(stmt)
    await session.commit()
