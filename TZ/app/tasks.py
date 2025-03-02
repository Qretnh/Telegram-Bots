from celery import shared_task
from .bot.main import send


@shared_task
def send_mailing_task(id, message, buttons=None):
    status = send(id, message, buttons)
    return status
