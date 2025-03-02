import datetime
import logging
import os
import pandas
import openpyxl
from django.conf import settings


def save_order_and_update_excel(items, price, phone_number, email, address, complete: int = 0):
    # Указываем путь к файлу
    file_path = os.path.join(settings.BASE_DIR, "Orders.xlsx")

    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        return

    try:
        # Загружаем книгу
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Создаём новую строку
        new_row = [
            items,
            price,
            phone_number,
            email,
            address,
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Форматируем дату
            complete
        ]
        sheet.append(new_row)

        # Сохраняем изменения
        workbook.save(file_path)

        # Логируем изменения
        df = pandas.read_excel(file_path)
        logging.info(f'В эксель добавлено: {df}')

    except PermissionError:
        print("Ошибка: файл заблокирован для записи. Закройте его в других программах.")
    except Exception as e:
        print(f"Ошибка при обновлении Excel-файла: {e}")