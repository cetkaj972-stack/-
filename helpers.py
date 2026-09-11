from datetime import datetime, timedelta
import random

# Фразы на 1-3 раз спама (вежливые)
SPAM_WARN_1 = [
    "мы тут честно играем, подожди {time}",
    "бля может ты подождёшь {time} и вернёшься?",
    "не спамь! Будь добр подождать {time}",
    "чел я знаю что ты хочешь карту получить поскорее, но время не прошло, возвращайся через {time}"
]

# Фразы на 4-7 раз спама (уже горит жопа)
SPAM_WARN_2 = [
    "бро ты совсем тупой? Я говорю подожди {time} !!!",
    "я повторять ещё не буду, подожди {time} ты меня достал",
    "балбесина ты слепой или чо ? Подожди {time} и возвращайся!"
]

# Фразы на 8+ раз спама (чистая ярость, шлём нах#й)
SPAM_WARN_3 = [
    "тупоролый, всё иди нах#й, тебе всё сказали",
    "за#бал, хватит др#чить эту команду!",
    "похоже кое кто слепошарый, продолжай позориться бля",
    "ого братан та ты прям баранище конкретный!"
]

def format_time_delta(td):
    """Красиво форматирует оставшееся время в минуты и секунды"""
    total_seconds = int(td.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes} мин. {seconds} сек."

def get_cooldown_message(spam_count, time_left_str):
    """Выбирает фразу в зависимости от того, какой раз спамит юзер"""
    if spam_count <= 3:
        phrase = random.choice(SPAM_WARN_1)
    elif spam_count <= 7:
        phrase = random.choice(SPAM_WARN_2)
    else:
        phrase = random.choice(SPAM_WARN_3)
    
    # Подставляем время в текст, если оно там требуется
    return phrase.replace("{time}", time_left_str)
