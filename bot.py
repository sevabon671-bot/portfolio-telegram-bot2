import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ------------------ НАСТРОЙКИ ------------------

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("TG_ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ------------------ ДАННЫЕ ------------------

PRODUCTS = {
    1: {"name": "Подписка на канал", "price": 500},
    2: {"name": "PDF-гайд", "price": 300},
    3: {"name": "Консультация", "price": 1500},
}

USER_CARTS = {}

# ------------------ КНОПКИ ------------------

def catalog_kb():
    kb = InlineKeyboardBuilder()
    for pid, product in PRODUCTS.items():
        kb.button(
            text=f"{product['name']} — {product['price']} ₽",
            callback_data=f"product_{pid}",
        )
    kb.adjust(1)
    return kb.as_markup()


def product_kb(pid: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ В корзину", callback_data=f"add_{pid}")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.adjust(1)
    return kb.as_markup()


def cart_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Оформить заказ", callback_data="order")
    kb.button(text="❌ Очистить корзину", callback_data="clear_cart")
    kb.adjust(1)
    return kb.as_markup()


def admin_kb(client_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✉️ Написать клиенту",
                    url=f"tg://user?id={client_id}",
                )
            ]
        ]
    )

# ------------------ ХЭНДЛЕРЫ ------------------

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Здравствуйте! 👋\n"
        "Выберите интересующий вас товар:",
        reply_markup=catalog_kb(),
    )


@dp.callback_query(F.data.startswith("product_"))
async def product_view(call: CallbackQuery):
    pid = int(call.data.split("_")[1])
    product = PRODUCTS[pid]

    await call.message.answer(
        f"📦 {product['name']}\n"
        f"💰 Цена: {product['price']} ₽",
        reply_markup=product_kb(pid),
    )
    await call.answer()


@dp.callback_query(F.data.startswith("add_"))
async def add_to_cart(call: CallbackQuery):
    USER_CARTS.setdefault(call.from_user.id, []).append(
        int(call.data.split("_")[1])
    )
    await call.answer("Добавлено в корзину")


@dp.callback_query(F.data == "cart")
async def show_cart(call: CallbackQuery):
    cart = USER_CARTS.get(call.from_user.id, [])

    if not cart:
        await call.message.answer("🛒 Корзина пуста.")
        await call.answer()
        return

    text = "🛒 Ваш заказ:\n\n"
    total = 0
    for pid in cart:
        p = PRODUCTS[pid]
        text += f"• {p['name']} — {p['price']} ₽\n"
        total += p["price"]

    text += f"\n💰 Итого: {total} ₽"

    await call.message.answer(text, reply_markup=cart_kb())
    await call.answer()


@dp.callback_query(F.data == "clear_cart")
async def clear_cart(call: CallbackQuery):
    USER_CARTS[call.from_user.id] = []
    await call.message.answer("❌ Корзина очищена.")
    await call.answer()


@dp.callback_query(F.data == "order")
async def make_order(call: CallbackQuery):
    user = call.from_user
    cart = USER_CARTS.get(user.id, [])

    if not cart:
        await call.answer("Корзина пуста", show_alert=True)
        return

    text = "🆕 <b>Новый заказ</b>\n\n"
    total = 0

    for pid in cart:
        p = PRODUCTS[pid]
        text += f"• {p['name']} — {p['price']} ₽\n"
        total += p["price"]

    text += f"\n💰 <b>Сумма:</b> {total} ₽"
    text += f"\n\n👤 Клиент: {user.full_name}"
    text += f"\n🆔 ID: <code>{user.id}</code>"
    if user.username:
        text += f"\n🔗 @{user.username}"

    await bot.send_message(
        ADMIN_ID,
        text,
        reply_markup=admin_kb(user.id),
        parse_mode="HTML",
    )

    USER_CARTS[user.id] = []

    await call.message.answer(
        "✅ Заказ принят!\n"
        "Менеджер свяжется с вами в ближайшее время."
    )
    await call.answer()

# ------------------ ЗАПУСК ------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
