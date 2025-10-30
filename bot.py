import logging
import os
import re
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_birth_date(player_name):
    url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{player_name}"
    r = requests.get(url)
    if r.status_code != 200:
        return "⚠️ Не удалось найти информацию."
    data = r.json()
    text = data.get("extract", "")
    match = re.search(r"родил[аc][ась]?\s*(\d{1,2}\s+[а-я]+\s+\d{4})", text)
    if match:
        return f"🎉 Родился {match.group(1)}"
    else:
        return "⚠️ Дата рождения не найдена."

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("⚽ Напиши имя футболиста (например: Салах, Месси, Роналду) — я скажу дату рождения!")

@dp.message()
async def handle_name(message: types.Message):
    player_name = message.text.strip().capitalize()
    reply = get_birth_date(player_name)
    await message.answer(reply)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
