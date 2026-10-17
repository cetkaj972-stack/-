import random
from shop_config import ITEMS

def calculate_next_level_xp(current_level):
    """
    Расчёт необходимого XP для следующего уровня.
    1 уровень: 5.0% XP (0.05).
    Каждый следующий уровень требует на 3.0% (0.03) больше.
    """
    if current_level == 1:
        return 0.05
    return 0.05 + (current_level - 1) * 0.03

def check_level_up(current_level, current_xp):
    """Проверка повышения уровня. Возвращает (новый_уровень, остаток_xp, поднялся_ли)"""
    leveled_up = False
    new_level = current_level
    new_xp = current_xp
    
    while True:
        required_xp = calculate_next_level_xp(new_level)
        if new_xp >= required_xp:
            new_xp -= required_xp
            new_level += 1
            leveled_up = True
        else:
            break
            
    return new_level, round(new_xp, 4), leveled_up

def wear_down_item(conn, user_id, item_type):
    """
    Отнимает 3-5% прочности у надетой шмотки.
    Если прочность падает до 0, шмотка ломается и удаляется.
    """
    cursor = conn.cursor()
    # Ищем надетую шмотку этого типа
    cursor.execute('''
        SELECT id, item_id, durability FROM inventory 
        WHERE user_id = ? AND item_type = ? AND is_equipped = 1
    ''', (user_id, item_type))
    
    item = cursor.fetchone()
    if not item:
        return None # Нет надетой шмотки
        
    item_db_id = item['id']
    item_id = item['item_id']
    current_dur = item['durability']
    
    # Собаки вечные (durability = inf), их не изнашиваем
    if current_dur == float('inf'):
        return None
        
    # Снижаем прочность на 3-5%
    wear = random.randint(3, 5)
    new_dur = max(0.0, current_dur - wear)
    
    if new_dur <= 0:
        # Шмотка сломалась — удаляем из инвентаря
        cursor.execute('DELETE FROM inventory WHERE id = ?', (item_db_id,))
        conn.commit()
        return f"🚨 Твой предмет '{ITEMS[item_type][item_id]['name']}' полностью сломался и развалился!"
    else:
        # Обновляем прочность в БД
        cursor.execute('UPDATE inventory SET durability = ? WHERE id = ?', (new_dur, item_db_id))
        conn.commit()
        return None
        from cards_config import CARDS, RARITY_CHANCES

def roll_card(equipped_items):
    """
    Рандомный выбор карты с учётом бустов от перчаток и кубиков.
    equipped_items: словарь активных шмоток юзера {type: id}
    """
    # 1. Считаем базовые шансы
    chances = RARITY_CHANCES.copy()
    
    # Считаем бусты удачи от перчаток и кубиков
    luck_boost = 0.0
    
    # Буст от перчаток
    if "gloves" in equipped_items:
        g_id = equipped_items["gloves"]
        luck_boost += ITEMS["gloves"][g_id].get("luck_boost", 0.0)
        
    # Буст от кубиков
    if "dice" in equipped_items:
        d_id = equipped_items["dice"]
        luck_boost += ITEMS["dice"][d_id].get("luck_boost", 0.0)
        
    # Применяем буст (снижаем шанс дефолтных карт в пользу редких, мификов и лег)
    if luck_boost > 0:
        boost_each = luck_boost / 3
        chances["common"] = max(0.10, chances["common"] - luck_boost)
        chances["rare"] += boost_each
        chances["mythic"] += boost_each
        chances["legendary"] += boost_each

    # 2. Роллим редкость
    rand_val = random.random()
    cumulative = 0.0
    chosen_rarity = "common"
    
    for rarity, chance in chances.items():
        cumulative += chance
        if rand_val <= cumulative:
            chosen_rarity = rarity
            break
            
    # 3. Выбираем случайную карту этой редкости
    possible_cards = [card_id for card_id, info in CARDS.items() if info["rarity"] == chosen_rarity]
    chosen_card_id = random.choice(possible_cards)
    
    return chosen_card_id

def calculate_rewards(chosen_card_id, equipped_items, is_subbed):
    """Расчёт итоговых наград (монеты, опыт) с учётом собак, машин и подписки"""
    card_info = CARDS[chosen_card_id]
    base_coins = card_info["coins"]
    base_xp = card_info["xp"]
    
    # --- 1. БУСТ МОНЕТ (СОБАКИ) ---
    coin_multiplier = 1.0
    if "dog" in equipped_items:
        dog_id = equipped_items["dog"]
        min_b, max_b = ITEMS["dog"][dog_id]["money_bonus_range"]
        # Рандомим процент буста в зависимости от собаки
        coin_multiplier += random.uniform(min_b, max_b)
        
    if is_subbed:
        coin_multiplier += 0.05 # +5% за подписку
        
    final_coins = int(base_coins * coin_multiplier)
    
    # --- 2. БУСТ ОПЫТА (МАШИНЫ) ---
    xp_multiplier = 1.0
    if "car" in equipped_items:
        car_id = equipped_items["car"]
        xp_multiplier += ITEMS["car"][car_id].get("xp_boost", 0.0)
        
    if is_subbed:
        xp_multiplier += 0.06 # +6% за подписку
        
    final_xp = round(base_xp * xp_multiplier, 4)
    
    return final_coins, final_xp
