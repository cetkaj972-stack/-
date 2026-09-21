   import sqlite3
   import os

   DB_PATH = "goyda.db"

   def get_db_connection():
       conn = sqlite3.connect(DB_PATH)
       conn.row_factory = sqlite3.Row
       return conn

   def init_db():
       conn = get_db_connection()
       cursor = conn.cursor()
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
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS inventory (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               user_id INTEGER,
               item_type TEXT,
               item_id TEXT,
               durability REAL,
               is_equipped INTEGER DEFAULT 0,
               FOREIGN KEY(user_id) REFERENCES users(user_id)
           )
       ''')
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS collection (
               user_id INTEGER,
               card_id TEXT,
               quantity INTEGER DEFAULT 0,
               PRIMARY KEY(user_id, card_id),
               FOREIGN KEY(user_id) REFERENCES users(user_id)
           )
       ''')
       conn.commit()
       conn.close()

   if not os.path.exists(DB_PATH):
       init_db()
   
