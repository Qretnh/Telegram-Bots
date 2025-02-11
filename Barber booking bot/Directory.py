from file import File


class Directory:
    """
    Класс, отвечающий за имитацию директории в файловой системе
    Методы:
    ------
    add(self, content) -> None:
        Добавление элемента в содержимое директории
    get_content(self, param=None) -> list:
        Получение содержимого из директории
    filenames(self, param=None) -> list:
        Вывод информации об именах файлов директории
    """

    def __init__(self, name: str, content=None, permissions='all', root=None):
        """
        Класс, отвечающий за инициализацию директории
        :param name: Название директории
        :param content:  Содержимое директории. Изначально: []
        :param permissions: Список пользователей с правами доступа. Изначально: all (Все пользователи). 'all' или ['user1', 'user2'...]
        :param root: Ссылка на родительский каталог. False в случае, если папка является корневой
        """

        self.name = name
        self.content = content if content else []
        self.permissions = permissions
        self.root = root

    def add(self, content) -> None:
        """
        Добавление элемента в содержимое директории
        :param content: содержимое - File / Directory
        :return:
        """

        if self.content is not None:
            self.content.append(content)
            pass
        else:
            self.content = content

    def get_content(self, param=None) -> list:
        """
        Получение содержимого из директории
        :param param: служебный параметр
        :return:
        """

        if param is None:
            return self.content
        if param == 'dir':
            return [item for item in self.content if type(item) == Directory]
        if param != 'dir':
            return [item for item in self.content if type(item) == File]

    def filenames(self, param=None) -> list:
        """
        Вывод информации об именах файлов директории
        :param param: служебный параметр
        :return:
        """

        if param is None:
            try:
                return [item.name for item in self.get_content()]
            except:
                return []
        if param == 'dir':
            try:
                return [item.name for item in self.get_content('dir')]
            except:
                return []
        else:
            try:
                return [item.name for item in self.get_content() if item not in self.get_content('dir')]
            except:
                return []