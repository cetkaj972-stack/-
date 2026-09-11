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
