import logging
import os
import re
import requests
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# === ⚙️ Функция для получения даты рождения футболиста через RapidAPI ===
def get_birth_date(player_name):
    url = "https://wikipedia-api3.p.rapidapi.com/wiki"
    headers = {
        "x-rapidapi-key": "3ed5fdda73mshfec256005e6f066p1a0e68jsn8a3add5d7863",  # твой ключ
        "x-rapidapi-host": "wikipedia-api3.p.rapidapi.com"
    }
    params = {"action": "get_summary", "title": player_name}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        # Проверяем содержимое
        extract = data.get("extract", "")
        if not extract:
            return "⚠️ Не удалось получить данные с Википедии."

        match = re.search(r"родил[аc][ась]?\s*(\d{1,2}\s+[а-я]+\s+\d{4})", extract)
        if match:
            return f"🎉 Родился {match.group(1)}"
        else:
            return "⚠️ Дата рождения не найдена."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Ошибка при подключении к API: {e}"

# === Телеграм команды ===
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("⚽ Напиши имя футболиста (например: Салах, Месси, Роналду) — я скажу дату рождения!")

@dp.message()
async def handle_name(message: types.Message):
    player_name = message.text.strip().capitalize()
    reply = get_birth_date(player_name)
    await message.answer(reply)

# === Flask для Render ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

async def main():
    threading.Thread(target=run_flask).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
