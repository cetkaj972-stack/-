python
import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from config import BOT_TOKEN

# Включаем логирование, чтобы видеть косяки в консоли
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация БД (сразу закладываем ВСЕ поля под будущие куски!)
def init_db():
    conn = sqlite3.connect("goyda_bot.db")
    cursor = conn.cursor()
    # Таблица юзеров
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            level REAL DEFAULT 0.0,
            last_card_time TEXT,
            spam_counter INTEGER DEFAULT 0,
            last_spam_time TEXT,
            sub_bonus_claimed_today INTEGER DEFAULT 0
        )
    """)
    # Таблица инвентаря (под кусок №3)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_type TEXT,
            item_name TEXT,
            durability REAL,
            is_active INTEGER DEFAULT 0
        )
    """)
    # Таблица коллекции (под кусок №6)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collection (
            user_id INTEGER,
            card_id INTEGER,
            quantity INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, card_id)
        )
    """)
    conn.commit()
    conn.close()

# Регистрация юзера в БД при любом взаимодействии
def register_user(user_id, username):
    conn = sqlite3.connect("goyda_bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

# --- КНОПКИ И МЕНЮ ---

def get_main_menu_keyboard():
    # Создаем жирные кнопки для главного меню
    kb = [
        [InlineKeyboardButton(text="🔥 СОБРАТЬ КАРТОЧКУ 🔥", callback_data="collect_card")],
        [
            InlineKeyboardButton(text="🏪 Магазин", callback_data="open_shop"),
            InlineKeyboardButton(text="🎒 Инвентарь", callback_data="open_inventory")
        ],
        [
            InlineKeyboardButton(text="🏆 Топы", callback_data="open_tops"),
            InlineKeyboardButton(text="🖼 Коллекция", callback_data="open_collection")
        ],
        [InlineKeyboardButton(text="📜 Список команд", callback_data="open_help")]
    ]
    return InlineKeyboardMar

kup(inline_keyboard=kb)

# --- ОБРАБОТЧИКИ (ХЕНДЛЕРЫ) ---

# Старт бота
@dp.message(CommandStart())
async def cmd_start(message: Message):
    register_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Здарова, бро {message.from_user.first_name}! 👋\n"
        f"Я Goyda Bot. Тут ты можешь собирать уникальные карты, качать лвл и скупать лютый шмот в магазине.\n"
        f"Пиши <b>менюшка</b>, чтобы открыть панель управления!",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )

# Триггер на "менюшка"
@dp.message(F.text.lower() == "менюшка")
async def show_menu_text(message: Message):
    register_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "Ты зашёл в главное меню, бро. Выбирай, чё делать будем:",
        reply_markup=get_main_menu_keyboard()
    )

# Триггеры на Сбор Карточки
CARD_TRIGGERS = ["нифес", "нефес", "получить карточку", "карту пж", "позязя карту", "гойда", "дай карту!"]

@dp.message(F.text.lower().in_(CARD_TRIGGERS))
async def trigger_collect_card(message: Message):
    register_user(message.from_user.id, message.from_user.username)
    await message.answer("⏳ Логика сбора карты настраивается... (Жди следующий кусок кода)")

# Триггеры на Магазин
SHOP_TRIGGERS = ["магаз", "магазинчик", "нифес магаз!", "дайте мне колбас!"]

@dp.message(F.text.lower().in_(SHOP_TRIGGERS))
async def trigger_shop(message: Message):
    register_user(message.from_user.id, message.from_user.username)
    await message.answer("🏪 Магазин откроется в Куске №3. Потерпи, бро!")

# Вспомогательное сообщение со списком команд
@dp.callback_query(F.data == "open_help")
async def callback_help(callback: CallbackQuery):
    help_text = (
        "📝 <b>Список команд (нажми, чтобы скопировать):</b>\n\n"
        "🟢 <u>Сбор карт (любое слово):</u>\n"
        "<code>нифес</code>\n"
        "<code>нефес</code>\n"
        "<code>получить карточку</code>\n"
        "<code>карту пж</code>\n"
        "<code>позязя карту</code>\n"
        "<code>Гойда</code>\n"
        "<code>дай карту!</code>\n\n"
        "🔵 <u>Магазин:</u>\n"
        "<code>магаз</code>\n"
        "<code>магазинчик</code>\n"
        "<code>нифес магаз!</code>\n"
        "<code>дайте мне колбас!</code>\n\n"
        "🟡 <u>Главное меню:</u>\n"
        "<code>менюшка</code>"
    )
    await callback.message.edit_text(help_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    await callback.answer()

# Заглушки для будущих кнопок
@dp.callback_query(F.data == "collect_card")
async def cb_collect_dummy(callback: CallbackQuery):
    await callback.answer("⏳ Сбор карты будет доступен в Куске №2 и №4!", show_alert=True)

@dp.callback_query(F.data == "open_shop")
async def cb_shop_dummy(callback: CallbackQuery):
    await callback.answer("🏪 Магазин будет доступен в Куске №3!", show_alert=True)

@dp.callback_query(F.data == "open_inventory")
async def cb_inv_dummy(callback: CallbackQuery):
    await callback.answer("🎒 Инвентарь будет доступен в Куске №6!", show_alert=True)

@dp.callback_query(F.data == "open_tops")
async def cb_tops_dummy(callback: CallbackQuery):
    await callback.answer("🏆 Топы будут доступны в Куске №6!", show_alert=True)

@dp.callback_query(F.data == "open_collection")
async def cb_coll_dummy(callback: CallbackQuery):
    await callback.answer("🖼 Коллекция будет доступна в Куске №6!", show_alert=True)

# Главный запуск
async def main():
    init_db()
    print("БД успешно проинициализирована!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
