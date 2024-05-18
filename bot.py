import aiogram
from config import TOKEN
from aiogram import Bot, Dispatcher
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from app.handlers import router

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройка логирования
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)  # Устанавливаем уровень логирования на ERROR

    # Настройка формата логов
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Создание обработчика для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)  # Устанавливаем уровень логирования на ERROR
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Создание обработчика для логирования в файл с ротацией
    file_handler = RotatingFileHandler('bot.log', maxBytes=5*1024*1024, backupCount=2)
    file_handler.setLevel(logging.ERROR)  # Устанавливаем уровень логирования на ERROR
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

async def main():
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    setup_logging()  # Настройка логирования
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Пока")
    except Exception as e:
        logging.exception("Произошла ошибка: %s", e)
