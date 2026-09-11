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
