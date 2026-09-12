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
