import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = ID  # твой telegram id

bot = Bot(TOKEN)
dp = Dispatcher()

# ------------------ ФЕЙКОВАЯ БАЗА ------------------

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
            text=f"{product['name']} — {product['price']}₽",
            callback_data=f"product_{pid}"
        )
    kb.adjust(1)
    return kb.as_markup()

def product_kb(pid):
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

# ------------------ ХЭНДЛЕРЫ ------------------

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🛍 Добро пожаловать в магазин!\n\nВыберите товар:",
        reply_markup=catalog_kb()
    )

@dp.callback_query(F.data.startswith("product_"))
async def product_view(call: CallbackQuery):
    pid = int(call.data.split("_")[1])
    product = PRODUCTS[pid]

    await call.message.answer(
        f"📦 <b>{product['name']}</b>\n"
        f"💰 Цена: {product['price']}₽",
        reply_markup=product_kb(pid),
        parse_mode="HTML"
    )
    await call.answer()

@dp.callback_query(F.data.startswith("add_"))
async def add_to_cart(call: CallbackQuery):
    pid = int(call.data.split("_")[1])
    user_id = call.from_user.id

    USER_CARTS.setdefault(user_id, [])
    USER_CARTS[user_id].append(pid)

    await call.answer("✅ Добавлено в корзину")

@dp.callback_query(F.data == "cart")
async def show_cart(call: CallbackQuery):
    user_id = call.from_user.id
    cart = USER_CARTS.get(user_id, [])

    if not cart:
        await call.message.answer("🛒 Корзина пуста")
        return

    text = "🛒 <b>Ваша корзина:</b>\n\n"
    total = 0

    for pid in cart:
        product = PRODUCTS[pid]
        text += f"• {product['name']} — {product['price']}₽\n"
        total += product["price"]

    text += f"\n💰 <b>Итого:</b> {total}₽"

    await call.message.answer(text, reply_markup=cart_kb(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "clear_cart")
async def clear_cart(call: CallbackQuery):
    USER_CARTS[call.from_user.id] = []
    await call.message.answer("❌ Корзина очищена")
    await call.answer()

@dp.callback_query(F.data == "order")
async def make_order(call: CallbackQuery):
    user = call.from_user
    cart = USER_CARTS.get(user.id, [])

    if not cart:
        await call.answer("Корзина пуста", show_alert=True)
        return

    text = "📩 <b>Новый заказ</b>\n\n"
    total = 0

    for pid in cart:
        product = PRODUCTS[pid]
        text += f"• {product['name']} — {product['price']}₽\n"
        total += product["price"]

    text += f"\n💰 Итого: {total}₽"
    text += f"\n👤 @{user.username or user.full_name}"

    await bot.send_message(ADMIN_ID, text, parse_mode="HTML")

    USER_CARTS[user.id] = []
    await call.message.answer("✅ Заказ отправлен! Мы скоро свяжемся с вами.")
    await call.answer()

# ------------------ ЗАПУСК ------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())






