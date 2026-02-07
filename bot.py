import os
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("8211878720:AAH4hdC3g1VvETD_idbNFnGWqyLsmv4jt6Y")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not API_TOKEN:
    raise ValueError("BOT_TOKEN not set")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID not set")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Бот работает ✅")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)



