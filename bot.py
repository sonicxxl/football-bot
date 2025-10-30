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

def get_birth_date(player_name):
    # Пробуем искать не только точное имя, но и первую найденную страницу
    search_url = f"https://ru.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": player_name,
        "utf8": "",
        "format": "json"
    }
    r = requests.get(search_url, params=params)
    if r.status_code != 200:
        return "⚠️ Не удалось получить данные с Википедии."

    data = r.json()
    results = data.get("query", {}).get("search", [])
    if not results:
        return "⚠️ Не удалось найти информацию."

    # Берем первую подходящую страницу
    title = results[0]["title"]
    url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{title}"
    r = requests.get(url)
    if r.status_code != 200:
        return "⚠️ Не удалось найти информацию."

    data = r.json()
    text = data.get("extract", "")
    match = re.search(r"родил[аc][ась]?\s*(\d{1,2}\s+[а-я]+\s+\d{4})", text)
    if match:
        return f"🎉 {title} родился {match.group(1)}"
    else:
        return f"⚠️ Дата рождения {title} не найдена."


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("⚽ Напиши имя футболиста (например: Салах, Месси, Роналду) — я скажу дату рождения!")

@dp.message()
async def handle_name(message: types.Message):
    player_name = message.text.strip().capitalize()
    reply = get_birth_date(player_name)
    await message.answer(reply)

# Flask web server for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running and connected to Render!"

def run_flask():
    # ⚠️ Используем порт из переменной окружения, как требует Render
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def main():
    threading.Thread(target=run_flask).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
