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
python
# ==================== ЛОГИКА ТАЙМЕРА И СБОРА КАРТЫ ====================

async def handle_get_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сбор бесплатной карточки с проверкой таймера и спама"""
    # Определяем, откуда пришёл запрос (кнопка или текст)
    query = update.callback_query
    if query:
        await query.answer()
        user = query.from_user
        chat = query.message.chat
    else:
        user = update.effective_user
        chat = update.effective_chat

    user_id = user.id
    username = user.username or user.first_name
    register_user_if_not_exists(user_id, username)

    # Проверяем подписку на ТГ канал для бонусов
    is_subbed = await check_tg_subscription(context.bot, user_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_card_time, level, coins, xp, spam_count, last_spam_time FROM users WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()

    # Считаем таймер с учётом надетой тачки
    equipped = get_user_equipped_items(user_id)
    base_cooldown = 50  # 50 минут по умолчанию
    
    if "car" in equipped:
        car_id = equipped["car"]
        reduction = ITEMS["car"][car_id].get("time_reduction", 0)
        cooldown_minutes = max(1, base_cooldown - reduction)
    else:
        cooldown_minutes = base_cooldown

    now = datetime.now()
    can_get_card = True
    time_left = timedelta(0)

    # Проверка времени последнего получения карты
    if player["last_card_time"]:
        last_time = datetime.fromisoformat(player["last_card_time"])
        next_time = last_time + timedelta(minutes=cooldown_minutes)
        if now < next_time:
            can_get_card = False
            time_left = next_time - now

    # ЕСЛИ ВРЕМЯ ЕЩЁ НЕ ПРОШЛО (СПАМ)
    if not can_get_card:
        spam_count = player["spam_count"] + 1
        time_left_str = format_time_delta(time_left)
        
        # Получаем матерную или вежливую фразу в зависимости от счётчика спама
        response_text = get_cooldown_message(spam_count, time_left_str)
        
        cursor.execute(
            "UPDATE users SET spam_count = ?, last_spam_time = ? WHERE user_id = ?",
            (spam_count, now.isoformat(), user_id)
        )
        conn.commit()
        conn.close()
        
        if query:
            await context.bot.send_message(chat_id=chat.id, text=response_text)
        else:
            await update.message.reply_text(response_text)
        return

    # ЕСЛИ ВСЁ ОК — ВЫДАЕМ КАРТУ!
    # Сбрасываем счётчик спама, так как лимит прошёл
    cursor.execute("UPDATE users SET spam_count = 0 WHERE user_id = ?", (user_id,))
    conn.commit()

    # Роллим карту и считаем награды
    chosen_card_id = roll_card(equipped)
    final_coins, final_xp = calculate_rewards(chosen_card_id, equipped, is_subbed)
    
    # Обновляем профиль игрока в БД
    new_xp = round(player["xp"] + final_xp, 4)
    new_level, remaining_xp, leveled_up = check_level_up(player["level"], new_xp)
    new_coins = player["coins"] + final_coins

    cursor.execute(
        "UPDATE users SET coins = ?, level = ?, xp = ?, last_card_time = ? WHERE user_id = ?",
        (new_coins, new_level, remaining_xp, now.isoformat(), user_id)
    )
    
    # Добавляем карту в коллекцию
    cursor.execute('''
        INSERT INTO collection (user_id, card_id, quantity) 
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, card_id) DO UPDATE SET quantity = quantity + 1
    ''', (user_id, chosen_card_id

))
    conn.commit()

    # Снижаем прочность надетых предметов (кроме бесконечных собак)
    break_messages = []
    for t in ["gloves", "domino", "dice", "car"]:
        break_msg = wear_down_item(conn, user_id, t)
        if break_msg:
            break_messages.append(break_msg)

    conn.close()

    # Формируем текст награды
    card_info = CARDS[chosen_card_id]
    reward_text = (
        f"🎉 {username}, ты получил карту:\n"
        f"✨ *{card_info['name']}* ({card_info['emoji']} {card_info['rarity'].upper()})\n\n"
        f"💰 Награда: +{final_coins} монет!\n"
        f"⭐ Опыт: +{final_xp}% XP!\n"
    )
    
    if leveled_up:
        reward_text += f"🆙 *УРОВЕНЬ ПОВЫШЕН! Твой новый уровень: {new_level}!* 🚀\n"
        
    if break_messages:
        reward_text += "\n" + "\n".join(break_messages)

    # Каждое 5-е успешное получение карты пиарим ТГ-канал (если ещё не подписан)
    if not is_subbed and random.random() < 0.20:
        reward_text += (
            f"\n\n🎁 Хочешь буст к заработку +5% монет, +6% опыта и 3 халявные карты без таймера каждый день? "
            f"Подписывайся на наш ТГ-канал: {TG_CHANNEL_URL}\n"
            f"Мы благодарны за подписку! Твоя поддержка помогает нам создавать игру мечты! ❤️"
        )

    # Отправляем картинку с описанием (картинка должна лежать в папке бота как png1.png ... png25.png)
    photo_path = f"{chosen_card_id}.png"
    if os.path.exists(photo_path):
        with open(photo_path, "rb") as photo:
            if query:
                await context.bot.send_photo(chat_id=chat.id, photo=photo, caption=reward_text, parse_mode="Markdown")
            else:
                await update.message.reply_photo(photo=photo, caption=reward_text, parse_mode="Markdown")
    else:
        # Если вдруг картинки нет на сервере, просто шлём текст
        msg = f"⚠️ [Картинка {photo_path} не найдена на сервере]\n\n" + reward_text
        if query:
            await context.bot.send_message(chat_id=chat.id, text=msg, parse_mode="Markdown")
        else:
            await update.message.reply_text(msg, parse_mode="Markdown")
