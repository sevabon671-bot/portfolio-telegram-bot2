import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")],
        [KeyboardButton(text="Оставить заявку")]
    ],
    resize_keyboard=True
)

TEXT = """
ДОРОГИЕ ТОВАРИЩИ❗

СЕГОДНЯ СОЗДАН ПРОЕКТ: partia game

РАЗЫГРЫВАЮТСЯ КОНФЕТЫ 🍬

КАК УЧАСТВОВАТЬ:
• Прическа с надписью PARTIA GAME
• Или плакат PARTIA GAME
• Упомянуть организаторов
• Или придумать свою идею

Нажмите «Оставить заявку».
"""

@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Добро пожаловать в partia game!", reply_markup=kb)

@dp.message(F.text == "Старт")
async def info(msg: Message):
    await msg.answer(TEXT)

@dp.message(F.text == "Оставить заявку")
async def apply(msg: Message):
    await msg.answer("Отправь текст или фото заявки.")

@dp.message()
async def forward(msg: Message):
    await bot.forward_message(ADMIN_ID, msg.chat.id, msg.message_id)
    await msg.answer("✅ Заявка отправлена!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
