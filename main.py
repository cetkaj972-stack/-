import sqlite3
import os

DB_PATH = "goyda.db"

def get_db_connection():
    """Быстрое подключение к базе данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Создание таблиц, если их ещё нет"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Таблица юзеров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            coins INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            xp REAL DEFAULT 0.0,
            last_card_time TEXT,
            spam_count INTEGER DEFAULT 0,
            last_spam_time TEXT,
            is_subscribed INTEGER DEFAULT 0
        )
    ''')

    # 2. Таблица инвентаря (вещи игрока)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_type TEXT, -- 'gloves', 'domino', 'dice', 'dog', 'car'
            item_id TEXT,   -- например, 'leather_gloves'
            durability REAL, -- текущая прочность в %
            is_equipped INTEGER DEFAULT 0, -- 1 - надето, 0 - в рюкзаке
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # 3. Таблица коллекции карт
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection (
            user_id INTEGER,
            card_id TEXT, -- 'png1' ... 'png25'
            quantity INTEGER DEFAULT 0,
            PRIMARY KEY(user_id, card_id),
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()

# Авто-инициализация при импорте файла
if not os.path.exists(DB_PATH):
    init_db()
