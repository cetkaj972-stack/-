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
