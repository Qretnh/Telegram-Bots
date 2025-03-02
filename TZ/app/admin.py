from django.contrib import admin
from django.utils.html import format_html
from .models import Categories, Orders, Products, Subcategories, Users
from app.tasks import send_mailing_task


@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',)
    actions = ['send_mailing']

    def mailing_action(self, obj):
        return format_html('<a class="button" href="{}">Отправить рассылку</a>', self.get_mailing_url(obj))

    mailing_action.short_description = 'Рассылка'
    mailing_action.allow_tags = True

    def send_mailing(self, request, queryset):
        # Получаем список ID пользователей
        user_ids = list(queryset.values_list('id', flat=True))

        # Сообщение и кнопки для рассылки
        message = "Ваше сообщение"
        buttons = [["Кнопка", "https://example.com"]]
        buttons = None
        for id in user_ids:
            send_mailing_task.delay(id, message, buttons)

        self.message_user(request, "Рассылка завершена")

    send_mailing.short_description = "Отправить рассылку через Telegram"


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('category',)

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    fields = ('phone_number', 'email', 'items', 'price', 'complete', 'address', 'time')  # Отображаемые поля
    list_display = ('phone_number', 'email', 'items', 'price', 'complete', 'address', 'time')
    list_editable = ('complete',)
    search_fields = ('phone_number', 'email')
    ordering = ('id',)


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'subcategory', 'name', 'price', 'description', 'photo_id')


@admin.register(Subcategories)
class SubcategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
