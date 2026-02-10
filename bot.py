import asyncio
import os
from datetime import datetime, timedelta
from collections import defaultdict

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramRetryAfter

import aiosqlite
from dotenv import load_dotenv

# ---------- ЗАГРУЗКА НАСТРОЕК ----------
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS").split(",")]

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_NAME = "partia.db"

# ---------- НАСТРОЙКИ ----------
COOLDOWN_MINUTES = 5     # пауза между заявками
SPAM_LIMIT = 20          # сообщений
SPAM_WINDOW_SEC = 30     # за сколько секунд
BAN_TIME_MIN = 60        # бан

# ---------- ПАМЯТЬ ----------
user_last_apply = {}
user_messages = defaultdict(list)
banned_users = {}

# ---------- КНОПКИ ----------
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")],
        [KeyboardButton(text="Оставить заявку")]
    ],
    resize_keyboard=True
)

TEXT = """
ДОРОГИЕ ТОВАРИЩИ❗

Проект: partia game

Чтобы участвовать:
• прическа PARTIA GAME
• или плакат PARTIA GAME
• или своя идея

Нажмите «Оставить заявку».
"""

# ---------- БАЗА ----------
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            content_type TEXT,
            date TEXT
        )
        """)
        await db.commit()

async def save_application(user_id, username, content_type):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO applications (user_id, username, content_type, date) VALUES (?, ?, ?, ?)",
            (user_id, username, content_type, datetime.now().isoformat())
        )
        await db.commit()

# ---------- АНТИСПАМ ----------
async def check_ban(msg: Message):
    user_id = msg.from_user.id
    now = datetime.now()

    # активный бан
    if user_id in banned_users:
        if now < banned_users[user_id]:
            await msg.answer("🚫 Ты временно заблокирован за спам.")
            return True
        else:
            del banned_users[user_id]

    # считаем сообщения
    user_messages[user_id].append(now)
    user_messages[user_id] = [
        t for t in user_messages[user_id]
        if now - t < timedelta(seconds=SPAM_WINDOW_SEC)
    ]

    if len(user_messages[user_id]) >= SPAM_LIMIT:
        banned_users[user_id] = now + timedelta(minutes=BAN_TIME_MIN)
        user_messages[user_id].clear()
        await msg.answer("🚫 Бан на 60 минут за спам.")
        return True

    return False

# ---------- ХЕНДЛЕРЫ ----------
@dp.message(CommandStart())
async def start(msg: Message):
    if await check_ban(msg):
        return
    await msg.answer("Добро пожаловать в partia game!", reply_markup=kb)

@dp.message(F.text == "Старт")
async def info(msg: Message):
    if await check_ban(msg):
        return
    await msg.answer(TEXT)

@dp.message(F.text == "Оставить заявку")
async def apply(msg: Message):
    if await check_ban(msg):
        return
    await msg.answer("Отправь текст или фото заявки.")

@dp.message()
async def handle(msg: Message):
    if await check_ban(msg):
        return

    user_id = msg.from_user.id
    username = msg.from_user.username or "без username"

    # лимит заявок
    now = datetime.now()
    if user_id in user_last_apply:
        delta = now - user_last_apply[user_id]
        if delta < timedelta(minutes=COOLDOWN_MINUTES):
            wait = COOLDOWN_MINUTES - int(delta.total_seconds() // 60)
            await msg.answer(f"⏳ Подожди {wait} мин перед новой заявкой.")
            return

    user_last_apply[user_id] = now

    # тип контента
    if msg.photo:
        content = "photo"
    elif msg.text:
        content = "text"
    else:
        content = "other"

    # сохранение
    await save_application(user_id, username, content)

    # отправка админам
    for admin in ADMIN_IDS:
        try:
            await bot.forward_message(admin, msg.chat.id, msg.message_id)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await bot.forward_message(admin, msg.chat.id, msg.message_id)

    await msg.answer("✅ Заявка принята!")

# ---------- СТАТИСТИКА ----------
@dp.message(F.text == "/stats")
async def stats(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM applications")
        count = (await cursor.fetchone())[0]

    await msg.answer(f"📊 Всего заявок: {count}")

# ---------- ЗАПУСК ----------
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
