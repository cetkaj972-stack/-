python
import asyncio
import os
import random
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Токен берем из переменных окружения (Environment variables)
TOKEN = os.getenv("BOT_TOKEN", "СЮДА_СВОЙ_ТОКЕН_ЕСЛИ_ТЕСТИТЬ_ЛОКАЛЬНО")

bot = Bot(token=TOKEN)
dp = Dispatcher()

CARDS = {
    1: {"name": "Нифес #1", "rarity": "Редкая", "description": "нифес в пещере"},
    2: {
        "name": "Нифес #2",
        "rarity": "Мифическая",
        "description": "нифес в мрачном лесу",
    },
    3: {
        "name": "Нифес #3",
        "rarity": "Дефолтная",
        "description": "нифес в контейнере",
    },
    4: {
        "name": "Нифес #4",
        "rarity": "Легендарная",
        "description": "нифес на фоне заката",
    },
    5: {
        "name": "Нифес #5",
        "rarity": "Дефолтная",
        "description": "нифес в комоде",
    },
    6: {
        "name": "Нифес #6",
        "rarity": "Дефолтная",
        "description": "нифес в большом капюшоне",
    },
    7: {"name": "Нифес #7", "rarity": "Легендарная", "description": "техничка"},
    8: {"name": "Нифес #8", "rarity": "Редкая", "description": "нифес в горшке"},
    9: {
        "name": "Нифес #9",
        "rarity": "Мифическая",
        "description": "нифес на пляже",
    },
    10: {
        "name": "Нифес #10",
        "rarity": "Редкая",
        "description": "нифес смотрит в глазок",
    },
    11: {"name": "Нифес #11", "rarity": "Редкая", "description": "нифес и кофе"},
    12: {
        "name": "Нифес #12",
        "rarity": "Мифическая",
        "description": "нифес в лапах треножника",
    },
    13: {
        "name": "Нифес #13",
        "rarity": "Дефолтная",
        "description": "нифес на кровати",
    },
    14: {
        "name": "Нифес #14",
        "rarity": "Редкая",
        "description": "Муся это ты ?",
    },
    15: {
        "name": "Нифес #15",
        "rarity": "Дефолтная",
        "description": "нифес упал(а) с большой высоты",
    },
    16: {
        "name": "Нифес #16",
        "rarity": "Мифическая",
        "description": "нифес на фоне большой фабрики",
    },
    17: {
        "name": "Нифес #17",
        "rarity": "Легендарная",
        "description": "нифес на машине",
    },
    18: {"name": "Нифес #18", "rarity": "Редка

я", "description": "жуткая нифес"},
    19: {
        "name": "Нифес #19",
        "rarity": "Мифическая",
        "description": "нифес в киберпанк",
    },
    20: {
        "name": "Нифес #20",
        "rarity": "Редкая",
        "description": "нифес в тачке",
    },
    21: {
        "name": "Нифес #21",
        "rarity": "Мифическая",
        "description": "нифес фескер",
    },
    22: {
        "name": "Нифес #22",
        "rarity": "Редкая",
        "description": "нифес на Nissan Patrol Y61",
    },
    23: {
        "name": "Нифес #23",
        "rarity": "Редкая",
        "description": "нифес в во все тяжкие",
    },
    24: {
        "name": "Нифес #24",
        "rarity": "Дефолтная",
        "description": "нифес делает додеп",
    },
    25: {
        "name": "Нифес #25",
        "rarity": "Легендарная",
        "description": "нифес на криповом вайбе",
    },
}


async def init_db():
    async with aiosqlite.connect("cards.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            coins INTEGER DEFAULT 1000,
            opened INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            card_id INTEGER
        )
        """)
        await db.commit()


def get_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎴 Открыть кейс")
    builder.button(text="👤 Профиль")
    builder.button(text="🎒 Инвентарь")
    builder.button(text="🏆 Топ")
    builder.button(text="🛒 Магазин")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


async def register_user(user_id, username):
    async with aiosqlite.connect("cards.db") as db:
        cursor = await db.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
        )
        user = await cursor.fetchone()
        if not user:
            await db.execute(
                "INSERT INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username),
            )
            await db.commit()


async def get_random_card():
    roll = random.randint(1, 100)
    if roll <= 60:
        rarity = "Дефолтная"
    elif roll <= 85:
        rarity = "Редкая"
    elif roll <= 95:
        rarity = "Мифическая"
    else:
        rarity = "Легендарная"

    possible = [
        card_id
        for card_id, card in CARDS.items()
        if card["rarity"] == rarity
    ]
    if not possible:
        possible = list(CARDS.keys())

    return random.choice(possible)


@dp.message(Command("start"))
async def start(message: Message):
    await register_user(message.from_user.id, message.from_user.username)
    text = (
        "🎴 Добро пожаловать в бот карточек Нифес!\n\n"
        "Открывай кейсы, собирай коллекцию и поднимайся в топ."
    )
    await message.answer(text, reply_markup=get_keyboard())


@dp.message(F.text == "🛒 Магазин")
async def shop(message: Message):
    text = (
        "🛒 Магазин\n\n1 кейс = 100 монет\nДля открытия нажми: 🎴 Открыть кейс"
    )
    await message.answer(text)


@dp.message(F.text == "🎴 Открыть кейс")
async def open_case(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("cards.db") as db:
        cursor = await db.execute(
            "SELECT coins FROM users WHERE user_id = ?", (user_id,)
        )
        user = await cursor.fetchone()

        if not user or user[0] < 100:
            await message.answer("❌ Недостаточно монет")
            return

        card_id = await get_random_card()

        await db.execute(
            "UPDATE users SET coins = coins - 100, opened = opened + 1 WHERE user_id = ?",
            (user_id,),
        )
        await db.execute(
            "INSERT INTO inventory (user_id, card_id) VALUES (?, ?)",
            (user_id, card_id),
        )
        await db.commit()

    card = CARDS[card_id]
    text = (
        f"🎉 Тебе выпала карточка!\n\n"

f"📌 {card['name']}\n"
        f"⭐ Редкость: {card['rarity']}\n"
        f"📝 {card['description']}"
    )

    photo_path = f"cards/{card_id}.png"
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo, caption=text)
    else:
        await message.answer(
            f"{text}\n\n*(Картинка не найдена на сервере)*", parse_mode="Markdown"
        )


@dp.message(F.text == "👤 Профиль")
async def profile(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("cards.db") as db:
        cursor = await db.execute(
            "SELECT coins, opened FROM users WHERE user_id = ?", (user_id,)
        )
        user = await cursor.fetchone()

        cursor = await db.execute(
            "SELECT COUNT(*) FROM inventory WHERE user_id = ?", (user_id,)
        )
        cards_count = await cursor.fetchone()

    if user:
        text = (
            f"👤 Профиль\n\n"
            f"💰 Монеты: {user[0]}\n"
            f"🎴 Карточек: {cards_count[0]}\n"
            f"📦 Открыто кейсов: {user[1]}"
        )
    else:
        text = "Запусти бота через /start"

    await message.answer(text)


@dp.message(F.text == "🎒 Инвентарь")
async def inventory(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("cards.db") as db:
        cursor = await db.execute(
            "SELECT card_id FROM inventory WHERE user_id = ?", (user_id,)
        )
        cards = await cursor.fetchall()

    if not cards:
        await message.answer("🎴 Инвентарь пуст")
        return

    text = "🎒 Твои карточки:\n\n"
    for item in cards:
        card = CARDS[item[0]]
        text += f"• {card['name']} — {card['rarity']}\n"

    # Если инвентарь слишком большой, телега выдаст ошибку, но пока пофиг
    await message.answer(text)


@dp.message(F.text == "🏆 Топ")
async def top_players(message: Message):
    async with aiosqlite.connect("cards.db") as db:
        cursor = await db.execute(
            "SELECT username, opened FROM users ORDER BY opened DESC LIMIT 10"
        )
        users = await cursor.fetchall()

    text = "🏆 Топ игроков:\n\n"
    for index, user in enumerate(users, start=1):
        username = user[0] or "Без ника"
        text += f"{index}. @{username} — {user[1]} кейсов\n"

    await message.answer(text)


async def main():
    await init_db()
    # Сбрасываем старые накопившиеся сообщения, чтоб бот не сошел с ума при старте
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
