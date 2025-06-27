from aiogram.fsm.state import StatesGroup, State


class Search(StatesGroup):
    title = State()
    #user_id = State()

class AddFavorite(StatesGroup):
    title = State()
    #user_id = State()


class RemoveFavorite(StatesGroup):
    title = State()


class Favorites(StatesGroup):
    #user_id = State()
    games = State()  # Исправлено: добавлены скобки для вызова State
    result = State()


# class Story(StatesGroup):
#     user_id = State()
