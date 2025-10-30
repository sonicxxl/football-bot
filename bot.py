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


# ---- функция для поиска даты рождения ----
def get_birth_date(player_name):
    # прокси для обхода блокировок Render
    proxies = {
        "http": "http://proxy.scrapeops.io:8080",
        "https": "http://proxy.scrapeops.io:8080"
    }

    # сначала ищем имя на Википедии
    search_url = "https://ru.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": player_name,
        "utf8": "",
        "format": "json"
    }

    try:
        r = requests.get(search_url, params=params, proxies=proxies, timeout=10)
    except Exception as e:
        return f"⚠️ Ошибка при подключении к Википедии: {e}"

    if r.status_code != 200:
        return "⚠️ Не удалось получить данные с Википедии."

    data = r.json()
    results = data.get("query", {}).get("search", [])
    if not results:
        return "⚠️ Не удалось найти информацию."

    # берём первую найденную страницу
    title = results[0]["title"]
    url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{title}"

    try:
        r = requests.get(url, proxies=proxies, timeout=10)
    except Exception as e:
        return f"⚠️ Ошибка при запросе страницы: {e}"

    if r.status_code != 200:
        return "⚠️ Не удалось получить страницу Википедии."

    data = r.json()
    text = data.get("extract", "")

    # ищем дату рождения в тексте
    match = re.search(r"родил[аc][ась]?\s*(\d{1,2}\s+[а-я]+\s+\d{4})", text)
    if match:
        return f"🎉 {title} родился {match.group(1)}"
    else:
        return f"⚠️ Дата рождения {title} не найдена."


# ---- команды бота ----
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("⚽ Напиши имя футболиста (например: Салах, Месси, Роналду) — я скажу дату рождения!")


@dp.message()
async def handle_name(message: types.Message):
    player_name = message.text.strip().capitalize()
    reply = get_birth_date(player_name)
    await message.answer(reply)


# ---- Flask веб-сервер для Render ----
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running and connected to Render!"

def run_flask():
    # Render требует порт из переменной окружения
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ---- запуск ----
async def main():
    threading.Thread(target=run_flask).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
