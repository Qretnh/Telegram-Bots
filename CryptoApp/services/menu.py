menu_buttons = ['Перейти в приложение (айфрейм сайта)',
                'Скачать автоматику на телефон',
                'Перейти на сайт',
                'Техническая поддержка',
                'Банковские приложения']


def check_cb(text: str):
    if text == 'to_app':
        return 0
    if text == 'download':
        return 1
    if text == 'site':
        return 2
    if text == 'support':
        return 3
    if text == 'banks':
        return 4
