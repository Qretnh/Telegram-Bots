from sqlalchemy import ForeignKey, BIGINT, TEXT, INT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# создание моделей для SQLAlchemy

class Base(DeclarativeBase):
    pass


class Catalog(Base):
    __tablename__ = "categories"

    category: Mapped[str] = mapped_column(TEXT, primary_key=True)


class SubCategory(Base):
    __tablename__ = "subcategories"

    name: Mapped[str] = mapped_column(TEXT, primary_key=True)
    category: Mapped[str] = mapped_column(ForeignKey("categories.category"))


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(INT, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(ForeignKey("categories.category"))
    subcategory: Mapped[str] = mapped_column(ForeignKey("subcategories.name"))
    name: Mapped[str] = mapped_column(TEXT)
    price: Mapped[int] = mapped_column(INT)
    description: Mapped[str] = mapped_column(TEXT)
    photo_id: Mapped[str] = mapped_column(TEXT)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(INT, primary_key=True, autoincrement=True)
    items: Mapped[str] = mapped_column(TEXT)
    price: Mapped[int] = mapped_column(INT)
    phone_number: Mapped[int] = mapped_column(BIGINT)
    email: Mapped[str] = mapped_column(TEXT)
    address: Mapped[str] = mapped_column(TEXT)
    time: Mapped[str] = mapped_column(TEXT)
    complete: Mapped[int] = mapped_column(INT)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
