import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from db.database import Database  # Убедитесь, что у вас есть эта модель для работы с БД
from handlers import router# Подключаем роутер для обработки сообщений
import config  # Ваши настройки конфигурации

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


# Установка команд для бота
async def set_commands():
    # Список команд для бота
    commands = [
        BotCommand(command="start", description="Старт"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="favorites", description="Избранное"),
        BotCommand(command="history", description="История поиска"),  # Добавьте другие команды, если нужно
        BotCommand(command="search_game", description="Искать игру"),
        BotCommand(command="remove_favorite", description="Удалить из избранного"),
        BotCommand(command="add_favorite", description="Добавить в избранное"),
    ]


# Устанавливаем команды для всех пользователей
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Инициализация бота
async def start():
    await set_commands()  # Устанавливаем команды при запуске бота


# Основная функция для старта бота
async def main():
    # Создание моделей базы данных, если их еще нет
    Database.create_models()

    # Подключаем роутер для обработки сообщений
    dp.include_router(router)

    # Регистрируем асинхронную функцию старта
    dp.startup.register(start)

    # Удаляем webhook, если он был настроен, и начинаем polling
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем polling для получения обновлений
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Устанавливаем уровень логирования для отладки

    # Запуск бота
    try:
        asyncio.run(main())  # Запуск основной асинхронной функции
    except KeyboardInterrupt:
        print("Бот завершил работу.")

