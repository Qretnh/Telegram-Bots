import asyncio
import aiosqlite
from datetime import datetime, date
from sqlalchemy import ForeignKey, Date, DATE, DateTime, DATETIME, BIGINT, TEXT, BigInteger, INT, TIME
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.schema import CreateTable

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    phone_number: Mapped[int] = mapped_column(BIGINT)
    username: Mapped[str] = mapped_column(TEXT)
    tg_username: Mapped[str] = mapped_column(TEXT)


class Master(Base):
    __tablename__ = 'masters'

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(TEXT,nullable=True)
    description: Mapped[str] = mapped_column(TEXT, nullable=True)
    photo: Mapped[str] = mapped_column(TEXT, nullable=True)


class Admin(Base):
    __tablename__ = 'admins'

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)


class Ban(Base):
    __tablename__ = 'bans'

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)


class Service(Base):
    __tablename__ = 'services'

    unique_id: Mapped[int] = mapped_column(INT, autoincrement="ignore_fk", primary_key=True)

    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('masters.user_id'))
    price: Mapped[int] = mapped_column(BIGINT)
    name: Mapped[str] = mapped_column(TEXT)
    description: Mapped[str] = mapped_column(TEXT)
    length: Mapped[int] = mapped_column(INT)


class Record(Base):
    __tablename__ = 'records'

    unique_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(TEXT)
    master: Mapped[int] = mapped_column(BIGINT, ForeignKey('masters.user_id'))
    price: Mapped[int] = mapped_column(BIGINT)
    length: Mapped[int] = mapped_column(INT)
    date: Mapped[int] = mapped_column(DATE)
    time: Mapped[int] = mapped_column(TEXT)
    client_id: Mapped[int] = mapped_column(BIGINT)


class BasicInfo(Base):
    __tablename__ = 'information'

    id: Mapped[int] = mapped_column(INT, autoincrement="ignore_fk", primary_key=True)
    start_hour: Mapped[int] = mapped_column(INT, default=9)
    last_hour: Mapped[int] = mapped_column(INT, default=22)
    timezone: Mapped[int] = mapped_column(INT, default=0)


class WorkShift(Base):
    __tablename__ = 'work_shifts'

    unique_id: Mapped[int] = mapped_column(INT, autoincrement="ignore_fk", primary_key=True)
    master_id: Mapped[int] = mapped_column(INT)
    date: Mapped[datetime] = mapped_column(DATE)
    start_time: Mapped[int] = mapped_column(INT)
    end_time: Mapped[int] = mapped_column(INT)
