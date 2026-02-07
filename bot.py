import os
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(msg):
    await msg.answer("Бот работает ✅")

if __name__ == "__main__":
    executor.start_polling(dp)





