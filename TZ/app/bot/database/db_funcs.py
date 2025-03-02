from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pginsert
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Catalog, SubCategory, Product, Order, User


# функции для работы с бд через бота и sqlalchemy

async def get_catalog(
        session: AsyncSession
):
    stmt = select(Catalog)
    result = await session.execute(stmt)
    result = [item.category for item in result.scalars().all()]
    return result


async def get_subcategories(
        session: AsyncSession,
        category: str
):
    stmt = select(SubCategory).where(SubCategory.category == category)
    result = await session.execute(stmt)
    result = [item.name for item in result.scalars().all()]
    return result


async def get_products(
        session: AsyncSession,
        category: str,
        subcategory: str
):
    stmt = select(Product).where(Product.category == category, Product.subcategory == subcategory)
    result = await session.execute(stmt)
    result = [item.name for item in result.scalars().all()]
    return result


async def get_current_product(
        session: AsyncSession,
        category: str,
        subcategory: str,
        name: str
):
    stmt = select(Product).where(Product.category == category,
                                 Product.subcategory == subcategory,
                                 Product.name == name)
    result = await session.execute(stmt)
    result = [(item.name, item.price, item.description, item.photo_id, item.id) for item in result.scalars().all()]
    return result[0]


async def get_all_products(
        session: AsyncSession,
):
    stmt = select(Product)
    result = await session.execute(stmt)
    result = [(item.name, item.price, item.description, item.photo_id, item.id) for item in result.scalars().all()]
    return result


async def update_order(session: AsyncSession,
                       info: str,
                       price: int,
                       phone_number: int,
                       email: str,
                       address: str,
                       time: str):
    stmt = insert(Order).values(
        items=info,
        price=price,
        phone_number=phone_number,
        email=email,
        address=address,
        time=time,
        complete=0
    )
    await session.execute(stmt)
    await session.commit()


async def add_to_users(session: AsyncSession,
                       id: int):
    stmt = pginsert(User).values(id=id)
    stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
    await session.execute(stmt)
    await session.commit()
