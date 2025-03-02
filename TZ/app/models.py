from django.db import models


class Users(models.Model):
    id = models.BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Categories(models.Model):
    category = models.TextField(primary_key=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Orders(models.Model):
    items = models.TextField()
    price = models.IntegerField()
    phone_number = models.BigIntegerField()
    email = models.TextField()
    address = models.TextField()
    time = models.TextField()
    complete = models.IntegerField()

    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Products(models.Model):
    category = models.ForeignKey(Categories, models.DO_NOTHING, db_column='category')
    subcategory = models.ForeignKey('Subcategories', models.DO_NOTHING, db_column='subcategory')
    name = models.TextField()
    price = models.IntegerField()
    description = models.TextField()
    photo_id = models.TextField()

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Subcategories(models.Model):
    name = models.TextField(primary_key=True)
    category = models.ForeignKey(Categories, models.DO_NOTHING, db_column='category')

    class Meta:
        db_table = 'subcategories'
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
