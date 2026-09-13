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
            python
# ==================== ИНТЕРАКТИВНЫЙ МАГАЗИН ====================

async def handle_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открытие главного меню магазина"""
    query = update.callback_query
    text = "🛒 Добро пожаловать в магазин прокачки!\nЗдесь ты можешь купить перчатки, кубики, домино, псов и тачки.\n\nВыбери категорию:"
    if query:
        await query.answer()
        await query.edit_message_text(text, reply_markup=get_shop_categories_keyboard())
    else:
        await update.message.reply_text(text, reply_markup=get_shop_categories_keyboard())

async def handle_shop_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение товаров в выбранной категории"""
    query = update.callback_query
    await query.answer()
    
    category = query.data.split("_")[-1] # Получаем gloves, dice, domino, dog, car
    user_id = query.from_user.id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
    player_lvl = cursor.fetchone()["level"]
    conn.close()

    text = f"📦 Категория: *{category.upper()}*\n\n"
    keyboard = []
    
    # Перебираем все товары из shop_config.py
    for item_id, info in ITEMS[category].items():
        is_locked = player_lvl < info["min_level"]
        lock_icon = "🔒" if is_locked else "🛒"
        lvl_req = f" (Нужен {info['min_level']} лвл)" if is_locked else ""
        
        button_text = f"{lock_icon} {info['name']} — {info['price']} монет{lvl_req}"
        # Кнопка отправляет запрос на покупку
        callback_data = f"buy_req_{category}_{item_id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        text += f"▪️ *{info['name']}*\n↳ {info['desc']}\n↳ Цена: {info['price']} монет | Доступ со следующего уровня: {info['min_level']}\n\n"

    keyboard.append([InlineKeyboardButton("🔙 Назад в магазин", callback_data="menu_shop")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_buy_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос на подтверждение покупки"""
    query = update.callback_query
    await query.answer()
    
    _, _, item_type, item_id = query.data.split("_")
    info = ITEMS[item_type][item_id]
    
    text = f"❓ Ты уверен, что хочешь купить *{info['name']}* за {info['price']} монет?\n\nОписание: {info['desc']}"
    await query.edit_message_text(text, reply_markup=get_buy_keyboard(item_type, item_id, info["price"]), parse_mode="Markdown")

async def handle_buy_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка покупки и зачисление в БД"""
    query = update.callback_query
    await query.answer()
    
    _, _, item_type, item_id = query.data.split("_")
    info = ITEMS[item_type][item_id]
    user_id = query.from_user.id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем инфу об игроке
    cursor.execute("SELECT coins, level FROM users WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    
    if player["level"] < info["min_level"]:
        conn.close()
        await query.edit_message_text(f"❌ Твой уровень ({player['level']}) слишком мал! Требуется уровень {info['min_level']}.", reply_markup=get_shop_categories_keyboard())
        return
        
    if player["coins"] < info["price"]:
        conn.close()
        await query.edit_message_text(f"❌ Недостаточно монет! У тебя {player['coins']} монет, а нужно {info['price']}.", reply_markup=get_shop_categories_keyboard())
        return

    # Списываем монеты
    new_coins = player["coins"] - info["price"

]
    cursor.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_coins, user_id))
    
    # Начисляем вещь в инвентарь (прочность берем максимальную из конфига)
    cursor.execute('''
        INSERT INTO inventory (user_id, item_type, item_id, durability, is_equipped)
        VALUES (?, ?, ?, ?, 0)
    ''', (user_id, item_type, item_id, info["max_durability"]))
    
    conn.commit()
    conn.close()
    
    await query.edit_message_text(f"🎉 Успешная покупка! Ты приобрел *{info['name']}*! Вещь добавлена в твой инвентарь.", reply_markup=get_shop_categories_keyboard(), parse_mode="Markdown")
python
# ==================== ИНВЕНТАРЬ И КОЛЛЕКЦИЯ ====================

async def handle_inventory_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор категории инвентаря для просмотра вещей"""
    query = update.callback_query
    text = "🎒 *Твой инвентарь снаряжения*\nВыбери категорию, чтобы надеть или снять вещи:"
    
    keyboard = [
        [
            InlineKeyboardButton("🧤 Перчатки", callback_data="inv_cat_gloves"),
            InlineKeyboardButton("🎲 Кубики", callback_data="inv_cat_dice")
        ],
        [
            InlineKeyboardButton("🀄 Домино", callback_data="inv_cat_domino"),
            InlineKeyboardButton("🐕 Собаки", callback_data="inv_cat_dog")
        ],
        [
            InlineKeyboardButton("🚗 Машины", callback_data="inv_cat_car")
        ],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="menu_back")]
    ]
    
    if query:
        await query.answer()
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_inventory_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ вещей игрока в выбранной категории инвентаря"""
    query = update.callback_query
    await query.answer()
    
    category = query.data.split("_")[-1] # gloves, dice, domino, dog, car
    user_id = query.from_user.id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, item_id, durability, is_equipped FROM inventory WHERE user_id = ? AND item_type = ?",
        (user_id, category)
    )
    items = cursor.fetchall()
    conn.close()

    if not items:
        text = f"🎒 В категории *{category.upper()}* у тебя пока ничего нет. Купи что-нибудь в магазине!"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="menu_inventory")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    text = f"🎒 Твои предметы в категории *{category.upper()}*:\n\n"
    keyboard = []
    
    for item in items:
        info = ITEMS[category][item["item_id"]]
        status = "🟢 НАДЕТО" if item["is_equipped"] else "🔴 В рюкзаке"
        durability_str = f"{int(item['durability'])}%" if item["durability"] != float("inf") else "Вечный"
        
        text += f"▪️ *{info['name']}*\n↳ Состояние: {durability_str} | Статус: {status}\n\n"
        
        # Кнопка действия (надеть/снять)
        action_text = f"Снять {info['name']}" if item["is_equipped"] else f"Надеть {info['name']}"
        keyboard.append([InlineKeyboardButton(action_text, callback_data=f"inv_action_{item['id']}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_inventory")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_inventory_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Процесс надевания/снятия шмотки с автоматическим снятием старой вещи этого же типа"""
    query = update.callback_query
    await query.answer()
    
    db_id = int(query.data.split("_")[-1])
    user_id = query.from_user.id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Находим выбранный предмет
    cursor.execute("SELECT item_type, item_id, is_equipped FROM inventory WHERE id = ? AND user_id = ?", (db_id, user_id))
    item = cursor.fetchone()
    
    if not item:
        conn.close()
        await query.edit_message_text("❌ Предмет не найден!", reply_markup=get_back_to_menu_keyboard())
        return
        
    ite

m_type = item["item_type"]
    is_equipped = item["is_equipped"]
    
    if is_equipped:
        # Если вещь надета — просто снимаем её
        cursor.execute("UPDATE inventory SET is_equipped = 0 WHERE id = ?", (db_id,))
        msg = "🎒 Ты снял предмет."
    else:
        # Если вещь не надета — сначала снимаем ВСЕ другие вещи этого же типа, чтобы не стакались
        cursor.execute("UPDATE inventory SET is_equipped = 0 WHERE user_id = ? AND item_type = ?", (user_id, item_type))
        # Надеваем новую вещь
        cursor.execute("UPDATE inventory SET is_equipped = 1 WHERE id = ?", (db_id,))
        msg = f"🟢 Ты успешно экипировал предмет!"
        
    conn.commit()
    conn.close()
    
    await query.edit_message_text(msg, reply_markup=get_back_to_menu_keyboard())

async def handle_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр коллекции собранных карт игрока"""
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
    else:
        user_id = update.effective_user.id
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT card_id, quantity FROM collection WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    user_cards = {row["card_id"]: row["quantity"] for row in rows}
    
    text = "🖼 *Твоя коллекция карточек Нифес:*\n\n"
    total_unique = len(user_cards)
    
    # Красиво выводим список всех 25 карт
    for card_id, info in CARDS.items():
        qty = user_cards.get(card_id, 0)
        status_emoji = info["emoji"] if qty > 0 else "🔒"
        qty_text = f" — *{qty} шт.*" if qty > 0 else " — _Не выбита_"
        text += f"{status_emoji} *{info['name']}*{qty_text}\n"
        
    text += f"\n📊 Всего собрано уникальных карт: *{total_unique}/25*"
    
    if query:
        await query.edit_message_text(text, reply_markup=get_back_to_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=get_back_to_menu_keyboard(), parse_mode="Markdown")
