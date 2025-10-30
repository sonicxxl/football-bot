import logging
import os
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

RAPID_API_KEY = os.getenv("RAPID_API_KEY")

def get_birth_date(player_name):
    url = "https://wikipedia-api3.p.rapidapi.com/wiki"
    querystring = {"action": "get_summary", "title": player_name}
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "wikipedia-api3.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"⚠️ Ошибка при подключении к API: {e}"

    extract = data.get("summary", "")
    if not extract:
        return "⚠️ Не удалось получить данные с Википедии."

    import re
    match = re.search(r"(\d{1,2}\s+[а-я]+\s+\d{4})", extract)
    if match:
        return f"🎉 Родился {match.group(1)}"
    else:
        return f"⚽ {player_name}: дата рождения не найдена."

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("⚽ Напиши имя футболиста (например: Салах, Месси, Роналду) — я скажу дату рождения!")

@dp.message()
async def handle_name(message: types.Message):
    player_name = message.text.strip()
    reply = get_birth_date(player_name)
    await message.answer(reply)

# Flask сервер для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running with RapidAPI (Wikipedia API3)"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def main():
    threading.Thread(target=run_flask).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
