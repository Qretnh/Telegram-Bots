from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter

# Синхронное приложение для админки
sync_app = get_asgi_application()

# Асинхронное приложение для остальных частей
async_app = 'app'

application = ProtocolTypeRouter({
    "http": URLRouter([
        path("admin/", sync_app),  # Админка работает синхронно
        path("", async_app),       # Остальные части работают асинхронно
    ]),
})