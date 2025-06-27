from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def main_menu() -> ReplyKeyboardMarkup:
    """
    Создает и возвращает главное меню с кнопками для навигации.
    """

    # Создаем меню с двумя рядами кнопок
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Найти игру"), KeyboardButton(text="Помощь")],  # Первая строка с кнопками
            [KeyboardButton(text="История поиска"), KeyboardButton(text="Избранное")],  # Вторая строка с кнопками
            [KeyboardButton(text="Добавить игру"), KeyboardButton(text="Удалить из избранного")],  # Третья строка с кнопками
],
        resize_keyboard=True,  # Подстраивает размер клавиатуры под экран устройства
        input_field_placeholder="Используйте кнопки ниже",  # Подсказка в поле ввода
        one_time_keyboard=True,  # Клавиатура исчезнет после первого использования
    )

    # Возвращаем готовую клавиатуру
    return markup
