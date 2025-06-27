import typing
from functools import wraps

import requests
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest
from contextlib import suppress

from db.database import Database
import keyboards
import api
from states import Search, Favorites, AddFavorite, RemoveFavorite

router = Router()


def login_required(handler: typing.Callable) -> typing.Callable:
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        user = Database.get_user(message.from_user.username)
        if not user:
            return await message.answer(f"Пользователь не зарегистрирован.")

        result = await handler(message, *args, **kwargs)
        return result

    return wrapper


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = Database.get_user(message.from_user.username)
    if user:
        await message.answer(f"Привет {user.username}", reply_markup=keyboards.main_menu())
    else:
        user = Database.create_user(message.from_user.username)
        if not user:
            await message.answer(f"Произошла ошибка на сервере. Обратитесь позже")

        await message.answer(f"Привет {user.username}. Зарегистрировал вас", reply_markup=keyboards.main_menu())


@router.message(Command("help"))
@router.message(F.text == "Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "Привет, я помогаю искать и сохранять, чтобы ты не потерял интересующие"
        " игры из Steam Store.\n"
        "Я отвечаю на команды /search_game, /history, /favorites, /add_favorite, /remove_favorite\n"
        "/search_game - после этой команды, я буду искать игру в Steam Store, которую ты мне "
        "напишешь.\n"
        "/history - после этой команды, я покажу тебе когда и что ты просил меня найти.\n"
        "/add_favorite - после этой команды, я добавлю игру в избранное.\n"
        "/favorites - после этой команды, я покажу тебе сохраненные тобою игры.\n"
        "/remove_favorite - после этой команды я удалю игру из избранного.",
        reply_markup=keyboards.main_menu(),
    )

@router.message(Command("history"))
@router.message(F.text == "История поиска")
@login_required
async def cmd_history(message: Message):
    requests = Database.get_request_history(message.from_user.username, count=20)
    histories = []
    for i, r in enumerate(requests, start=1):
        history = f"{i}: {r.title}. {r.timestamp.strftime('%d.%m.%Y %H:%M:%S')}"
        histories.append(history)

    msg = f"История запросов:\n{'\n'.join(h for h in histories)}"
    await message.answer(msg)

@router.message(Command("favorites"))
@router.message(F.text == "Избранное")
@login_required
async def cmd_favorites(message: Message):
    req_favorites =Database.get_favorites(message.from_user.username, count=20)
    if not req_favorites:
        await message.answer("У вас пока нет избранных игр!")
        return
    text = ""
    for i, h in enumerate(req_favorites, start=1):
        text += f"{i}. {h.title}\n"
    await message.answer(text.strip())


@router.message(Command("remove_favorite"))
@router.message(F.text == "Удалить из избранного")
@login_required
async def cmd_delete_favorite(message: Message, state: FSMContext):
    await state.set_state(RemoveFavorite.title)
    await message.answer("Введите название игры")


@router.message(RemoveFavorite.title)
@login_required
async def cmd_delete_favorite(message: Message, state: FSMContext):
    favorite =Database.remove_from_favorites(message.from_user.username, message.text)
    await state.clear()
    if not favorite:
        await message.answer(f"Игра {message.text} не находится в избранном!")
        return

    await message.answer(f"Игра {message.text} удалена!")


@router.message(Command("search_game"))
@router.message(F.text == "Найти игру")
@login_required
async def cmd_search(message: Message, state: FSMContext):
    await state.set_state(Search.title)
    await message.answer("Введите название игры")


@router.message(Command("add_favorite"))
@router.message(F.text == "Добавить в избранное")
@login_required
async def cmd_add_favorite(message: Message, state: FSMContext):
    await state.set_state(AddFavorite.title)
    await message.answer(f"Введите название игры!")

@router.message(AddFavorite.title)
@login_required
async def cmd_add_favorite(message: Message, state: FSMContext):
    Database.add_to_favorites(message.from_user.username, message.text)
    await message.answer(f"Игра добавлена в избранное!")


@router.message(Search.title)
@login_required
async def search_games(message: Message, state: FSMContext):
    response = await api.search_games(term=message.text, page=1)
    Database.create_request_history(message.text, message.from_user.username)

    if not response:
        await message.answer(f"Простите, не нашел игр с таким названием - {message.text}")
        return

    # Отображаем данные первых 10 игр
    games = [
        f"Название: {game['title']}\nДата выхода: {game['released'].strip()}\nЦена: {game['price']}\nID: {game['app_id']}"
        for game in response[:10]]

    # Создаём красивое сообщение
    delimiter = len(max(games, key=len))
    text = f"\n*{'-' * delimiter}*\n".join(games)
    await state.clear()
    await message.answer(text)


