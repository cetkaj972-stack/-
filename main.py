import os
import sys
from datetime import datetime, timedelta
import random

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from database import get_db_connection, init_db
from shop_config import ITEMS
from keyboards import get_main_menu_keyboard, get_shop_categories_keyboard, get_back_to_menu_keyboard, get_inventory_keyboard, get_buy_keyboard
from helpers import get_cooldown_message, format_time_delta
from cards_config import CARDS
from game_logic import check_level_up, wear_down_item, roll_card, calculate_rewards

TG_CHANNEL_URL = "https://t.me/blood_robots_death"
CHANNEL_CHAT_ID = "@blood_robots_death"

if os.path.exists("token.txt"):
    with open("token.txt", "r") as f:
        BOT_TOKEN = f.read().strip()
else:
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

if not BOT_TOKEN:
    print("Ошибка: Токен не найден в token.txt!")
    sys.exit(1)
# ==================== РЕГИСТРАЦИЯ И ПОДПИСКА ====================

def register_user_if_not_exists(user_id, username):
    """Регистрация нового игрока в базе данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (user_id, username, coins, level, xp) VALUES (?, ?, 0, 1, 0.0)",
            (user_id, username)
        )
        conn.commit()
    conn.close()

async def check_tg_subscription(bot, user_id):
    """Проверка подписки на ТГ-канал blood_robots_death"""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_CHAT_ID, user_id=user_id)
        # Если статус участника не левый, то подписан
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    return False

def get_user_equipped_items(user_id):
    """Получить словарь надетых шмоток игрока"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT item_type, item_id FROM inventory WHERE user_id = ? AND is_equipped = 1",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return {row["item_type"]: row["item_id"] for row in rows}
