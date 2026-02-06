import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


# ================= НАСТРОЙКИ =================

import os



API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

# =============================================


# FSM состояния
class Form(StatesGroup):
    name = State()
    phone = State()
    comment = State()


# Инициализация
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# ================= ХЭНДЛЕРЫ =================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для приёма заявок.\n\n"
        "Как тебя зовут?"
    )
    await Form.name.set()


@dp.message_handler(state=Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📞 Введи номер телефона:")
    await Form.phone.set()


@dp.message_handler(state=Form.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("💬 Напиши комментарий:")
    await Form.comment.set()


@dp.message_handler(state=Form.comment)
async def get_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()

    text = (
        "📥 *Новая заявка*\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"💬 Комментарий: {message.text}"
    )

    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    await message.answer("✅ Спасибо! Заявка отправлена.")

    await state.finish()


# ================= ЗАПУСК =================

if __name__ == "__main__":
    print("🤖 Бот запущен и ждёт сообщения...")
    executor.start_polling(dp, skip_updates=True)
