from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu_keyboard():
    """Главное меню игры с жирной кнопкой сбора карт"""
    keyboard = [
        # Самая большая и важная кнопка сверху
        [InlineKeyboardButton("🔥 Собрать карточку! 🔥", callback_data="menu_get_card")],
        # Кнопки экономики и инвентаря
        [
            InlineKeyboardButton("🛒 Магазин", callback_data="menu_shop"),
            InlineKeyboardButton("🎒 Инвентарь", callback_data="menu_inventory")
        ],
        # Кнопки коллекции и топов
        [
            InlineKeyboardButton("🖼 Коллекция", callback_data="menu_collection"),
            InlineKeyboardButton("🏆 Топ игроков", callback_data="menu_leaderboard")
        ],
        # Список команд и слов (для копирования)
        [InlineKeyboardButton("📝 Список команд", callback_data="menu_commands")]
    ]
    return InlineKeyboardMarkup(keyboard)
    def get_shop_categories_keyboard():
    """Выбор категорий в магазине"""
    keyboard = [
        [
            InlineKeyboardButton("🧤 Перчатки", callback_data="shop_cat_gloves"),
            InlineKeyboardButton("🎲 Кубики", callback_data="shop_cat_dice")
        ],
        [
            InlineKeyboardButton("🀄 Домино", callback_data="shop_cat_domino"),
            InlineKeyboardButton("🐕 Собаки", callback_data="shop_cat_dog")
        ],
        [
            InlineKeyboardButton("🚗 Машины", callback_data="shop_cat_car")
        ],
        [
            InlineKeyboardButton("🔙 В главное меню", callback_data="menu_back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_menu_keyboard():
    """Простая кнопка возврата в меню"""
    keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="menu_back")]]
    return InlineKeyboardMarkup(keyboard)
    
def get_inventory_keyboard(items, item_type):
    """
    Кнопки для просмотра вещей в инвентаре.
    items: список вещей из БД
    item_type: категория ('gloves', 'dice', 'domino', 'dog', 'car')
    """
    keyboard = []
    # Для каждой шмотки в этой категории делаем кнопку
    for item in items:
        status = "🟢 Надето" if item['is_equipped'] else "🔴 Надеть"
        durability = f" ({int(item['durability'])}%)" if item['durability'] != float('inf') else " (Вечный)"
        
        # Кнопка действия (надеть/снять)
        action = f"equip_{item['id']}"
        keyboard.append([
            InlineKeyboardButton(f"{item['item_id'].capitalize()}{durability} | {status}", callback_data=action)
        ])
    
    # Кнопка возврата в меню
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="menu_back")])
    return InlineKeyboardMarkup(keyboard)

def get_buy_keyboard(item_type, item_id, price):
    """Кнопка подтверждения покупки шмотки"""
    keyboard = [
        [
            InlineKeyboardButton(f"✅ Купить за {price} монет", callback_data=f"buy_confirm_{item_type}_{item_id}"),
            InlineKeyboardButton("❌ Отмена", callback_data="menu_shop")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
