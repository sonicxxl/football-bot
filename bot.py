import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.exceptions import ConflictError

# === Настройки ===
BOT_TOKEN = "8213820981:AAHkls9iAujHNu126nX2d9ppdMJpvzMZoiA"  # вставь свой Telegram токен
RAPIDAPI_KEY = "3ed5fdda73mshfec256005e6f066p1a0e68jsn8a3add5d7863"

# === Логирование ===
logging.basicConfig(level=logging.INFO)

# === Инициализация бота ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# === Команда /start ===
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer("Привет! 🔍 Отправь мне любое слово, и я найду информацию из Википедии.")


# === Поиск статьи через Wikipedia API на RapidAPI ===
@dp.message_handler()
async def wiki_search(message: types.Message):
    query = message.text.strip()
    url = "https://wikipedia-api3.p.rapidapi.com/wiki"
    params = {"action": "get_summary", "title": query}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "wikipedia-api3.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            summary = data.get("summary", "❌ Ничего не найдено.")
            await message.answer(summary[:4000])  # Telegram лимит
        elif response.status_code == 404:
            await message.answer("⚠️ Статья не найдена.")
        elif response.status_code == 403:
            await message.answer("🚫 Ошибка 403: Проверь RapidAPI ключ и хост.")
        else:
            await message.answer(f"⚠️ Ошибка {response.status_code}: {response.text}")
    except Exception as e:
        await message.answer(f"❌ Ошибка при подключении к API: {e}")


# === Запуск с защитой от конфликтов polling ===
async def run_bot():
    print("🚀 Бот запускается... ждём 10 секунд, чтобы завершился старый процесс")
    await asyncio.sleep(10)

    while True:
        try:
            print("✅ Polling Telegram...")
            await dp.start_polling()
        except ConflictError:
            print("⚠️ Обнаружен конфликт polling — ждём 15 секунд и пробуем снова...")
            await asyncio.sleep(15)
        except Exception as e:
            print(f"❌ Ошибка: {e} — перезапуск через 20 секунд...")
            await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(run_bot())
