
class File:
    """
    Класс, выполняющий роль файла в имитации файловой системы
    """

    def __init__(self, name: str, permissions='all', extension='', root = None):
        """
        Класс, имитирующий файл в среде.
        :param name: Имя файла
        :param permissions: Права доступа для пользователей. all или {'access':'...', 'view':'...'}
        :param extension: расширение файла
        :param root: Директория, в которой файл хранится
        """
        if '.' in name:
            extension = name.split('.')[1]
        self.name = name
        self.extension = extension
        self.permissions = permissions
        self.root = root

    def info(self):
        """
        Вывод информации о файле
        :return:
        """
        return f'Filename: {self.name}\n' \
               f'Extension: {self.extension}\n' \
               f'Permissions: {self.permissions}'