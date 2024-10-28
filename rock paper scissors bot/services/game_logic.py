from random import choice


class stats:
    def __init__(self):
        self.info = {}

    def update(self, id, win):
        if id not in self.info.keys():
            self.info[id] = {'games': 0, 'wins': 0}
        self.info[id]['games'] += 1
        self.info[id]['wins'] += win

    def get_info(self, id):
        return self.info[id]['games'], \
            self.info[id]['wins']


statistics = stats()


def move(player_choice: str):
    bot_choice = choice(['Камень🪨', 'Ножницы✂️', 'Бумага📄'])
    if player_choice == bot_choice:
        result = "draw"
    elif (player_choice == 'Бумага📄' and bot_choice == 'Ножницы✂️') or (
            player_choice == 'Камень🪨' and bot_choice == 'Бумага📄') or (
            player_choice == 'Ножницы✂️' and bot_choice == 'Камень🪨'):
        result = "lose"
    else:
        result = "win"

    return result, bot_choice


def update_stats(id, win):
    statistics.update(id=id, win=win)


def stats(id):
    try:
        games, wins = statistics.get_info(id)
        return f"Сыграно игр: {games or 0}\n" \
               f"Побед: {wins}\n" \
               f"Процент побед: {int(round(wins / games, 2) * 100)}%\n" \
               f"Сыграем ещё?"
    except KeyError:
        return "Кажется, вы ещё не играли. Начнём?"
