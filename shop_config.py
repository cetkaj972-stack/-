# Базовый словарь магазина, куда мы по очереди вставим все предметы
ITEMS = {}

# ==================== 1. ПЕРЧАТКИ ====================
ITEMS["gloves"] = {
    "leather": {
        "name": "Кожаные перчатки",
        "price": 30,
        "min_level": 0,
        "max_durability": 30.0,
        "luck_boost": 0.05,
        "desc": "Прочность 30%. Удача +5%. Расход 3-5% за карту."
    },
    "reinforced": {
        "name": "Укреплённые перчатки",
        "price": 100,
        "min_level": 1,
        "max_durability": 50.0,
        "luck_boost": 0.10,
        "desc": "Прочность 50%. Удача +10%. Расход 3-5% за карту."
    },
    "magician": {
        "name": "Перчатки фокусника",
        "price": 150,
        "min_level": 1,
        "max_durability": 30.0,
        "luck_boost": 0.30,
        "desc": "Прочность 30%. Удача +30%. Расход 3-5% за карту."
    },
    "boxer": {
        "name": "Перчатки боксёра",
        "price": 150,
        "min_level": 5,
        "max_durability": 100.0,
        "luck_boost": 0.15,
        "desc": "Прочность 100%. Удача +15%. Расход 3-5% за карту."
    },
    "gold_gloves": {
        "name": "Золотые перчатки",
        "price": 250,
        "min_level": 10,
        "max_durability": 250.0,
        "luck_boost": 0.25,
        "desc": "Прочность 250%. Удача +25%. Расход 3-5% за карту."
    },
    "thanos": {
        "name": "Перчатка Таноса",
        "price": 1000,
        "min_level": 15,
        "max_durability": 5000.0,
        "luck_boost": 0.40,
        "desc": "Прочность 5000%. Удача +40%. Расход 3-5% за карту."
    }
}# ==================== 2. ДОМИНО ====================
ITEMS["domino"] = {
    "dark": {
        "name": "Домино тёмное",
        "price": 50,
        "min_level": 0,
        "max_durability": 50.0,
        "double_chance": 0.10,
        "desc": "Прочность 50%. Шанс на x2 карту: 10%."
    },
    "white": {
        "name": "Домино белое",
        "price": 50,
        "min_level": 1,
        "max_durability": 30.0,
        "double_chance": 0.20,
        "desc": "Прочность 30%. Шанс на x2 карту: 20%."
    },
    "wooden": {
        "name": "Домино деревянное",
        "price": 100,
        "min_level": 4,
        "max_durability": 80.0,
        "double_chance": 0.25,
        "desc": "Прочность 80%. Шанс на x2 карту: 25%."
    },
    "gold_domino": {
        "name": "Домино золотое",
        "price": 130,
        "min_level": 8,
        "max_durability": 120.0,
        "double_chance": 0.30,
        "desc": "Прочность 120%. Шанс на x2 карту: 30%."
    },
    "diamond": {
        "name": "Домино алмазное",
        "price": 500,
        "min_level": 30,
        "max_durability": 1000.0,
        "double_chance": 0.30,
        "desc": "Прочность 1000%. Шанс на x2 карту: 30%."
    }
}

# ==================== 3. КУБИКИ ====================
ITEMS["dice"] = {
    "normal": {
        "name": "Обычный кубик",
        "price": 60,
        "min_level": 1,
        "max_durability": 200.0,
        "luck_boost": 0.05,
        "desc": "Прочность 200%. Удача +5%."
    },
    "dark_dice": {
        "name": "Тёмный кубик",
        "price": 60,
        "min_level": 1,
        "max_durability": 100.0,
        "luck_boost": 0.10,
        "desc": "Прочность 100%. Удача +10%."
    },
    "pink": {
        "name": "Розовый кубик",
        "price": 65,
        "min_level": 1,
        "max_durability": 150.0,
        "luck_boost": 0.08,
        "desc": "Прочность 150%. Удача +8%."
    },
    "marble": {
        "name": "Мраморный кубик",
        "price": 150,
        "min_level": 8,
        "max_durability": 500.0,
        "luck_boost": 0.10,
        "desc": "Прочность 500%. Удача +10%."
    },
    "gold_dice": {
        "name": "Золотой кубик",
        "price": 500,
        "min_level": 15,
        "max_durability": 10000.0,
        "luck_boost": 0.15,
        "desc": "Прочность 10000%. Удача +15%."
        
    }
}
# ==================== 4. ПСЫ ====================
ITEMS["dog"] = {
    "chihuahua": {
        "name": "Чихуахуа",
        "price": 100,
        "min_level": 0,
        "max_durability": float('inf'),
        "money_bonus_range": (0.03, 0.10),
        "desc": "Прочность: Вечная. Буст голды: +3%..10%."
    },
    "mongrel": {
        "name": "Дворняга",
        "price": 500,
        "min_level": 3,
        "max_durability": float('inf'),
        "money_bonus_range": (0.05, 0.15),
        "desc": "Прочность: Вечная. Буст голды: +5%..15%."
    },
    "husky": {
        "name": "Хаски",
        "price": 1000,
        "min_level": 6,
        "max_durability": float('inf'),
        "money_bonus_range": (0.10, 0.20),
        "desc": "Прочность: Вечная. Буст голды: +10%..20%."
    },
    "shepherd": {
        "name": "Овчарка",
        "price": 2000,
        "min_level": 6,
        "max_durability": float('inf'),
        "money_bonus_range": (0.13, 0.30),
        "desc": "Прочность: Вечная. Буст голды: +13%..30%."
    },
    "german_shepherd": {
        "name": "Немецкая овчарка",
        "price": 5000,
        "min_level": 15,
        "max_durability": float('inf'),
        "money_bonus_range": (0.25, 0.50),
        "desc": "Прочность: Вечная. Буст голды: +25%..50%."
    },
    "alabai": {
        "name": "Алабай",
        "price": 4500,
        "min_level": 15,
        "max_durability": float('inf'),
        "money_bonus_range": (0.10, 1.00),
        "desc": "Прочность: Вечная. Буст голды: +10%..100%."
    }
}
# ==================== 5. МАШИНЫ ====================
ITEMS["car"] = {
    "zhiguli": {
        "name": "Жигули",
        "price": 300,
        "min_level": 1,
        "max_durability": 500.0,
        "time_reduction": 5,
        "xp_boost": 0.05,
        "desc": "Прочность 500%. Таймер: -5 мин. Опыт: +5%."
    },
    "lada_2110": {
        "name": "Lada (ВАЗ) 2110",
        "price": 400,
        "min_level": 5,
        "max_durability": 700.0,
        "time_reduction": 10,
        "xp_boost": 0.10,
        "desc": "Прочность 700%. Таймер: -10 мин. Опыт: +10%."
    },
    "bukhanka": {
        "name": "Буханка",
        "price": 500,
        "min_level": 6,
        "max_durability": 1500.0,
        "time_reduction": 12,
        "xp_boost": 0.08,
        "desc": "Прочность 1500%. Таймер: -12 мин. Опыт: +8%."
    },
    "lambo": {
        "name": "Ламборгини",
        "price": 6000,
        "min_level": 8,
        "max_durability": 200.0,
        "time_reduction": 35,
        "xp_boost": 0.15,
        "desc": "Прочность 200%. Таймер: -35 мин. Опыт: +15%."
    },
    "nissan": {
        "name": "Nissan Patrol Y61",
        "price": 2000,
        "min_level": 15,
        "max_durability": 6000.0,
        "time_reduction": 22,
        "xp_boost": 0.20,
        "desc": "Прочность 6000%. Таймер: -22 мин. Опыт: +20%."
    },
    "mercedes": {
        "name": "Мерседес",
        "price": 2100,
        "min_level": 12,
        "max_durability": 2000.0,
        "time_reduction": 18,
        "xp_boost": 0.25,
        "desc": "Прочность 2000%. Таймер: -18 мин. Опыт: +25%."
    }
}
