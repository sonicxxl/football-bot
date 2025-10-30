import logging
import os
import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def get_birth_date(player_name):
    url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{player_name}"
    r = requests.get(url)
    if r.status_code != 200:
        return "⚠️ Не удалось найти информацию."
    data = r.json()
    text = data.get("extract", "")
    match = re.search(r"родил[а-я]+(?:\\s+)(\\d{1,2}\\s+[а-я]+\\s+\\d{4})", text)
    if match:
        return f"📅 Родился {match.group(1)}"
    else:
        return "📭 Дата рождения не найдена."

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.answer("⚽ Напиши имя футболиста (например: Салах, Месси, Роналду) — я скажу дату рождения!")

@dp.message_handler()
async def handle_name(message: types.Message):
    name = message.text.strip().capitalize()
    info = get_birth_date(name)
    await message.answer(info)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
