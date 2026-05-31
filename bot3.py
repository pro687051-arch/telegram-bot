import telebot
import sqlite3
import random
from datetime import datetime

TOKEN = "8670467955:AAE-IPPIMaagq2AYEy-EF8QDYoZZur8brFE"
bot = telebot.TeleBot(TOKEN)

# База данных для памяти
def init_db():
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (user_id INTEGER, text TEXT, time TEXT)''')
    conn.commit()
    conn.close()

def save_message(user_id, text):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (user_id, text, time) VALUES (?, ?, ?)",
              (user_id, text, datetime.now().strftime("%H:%M:%S")))
    conn.commit()
    conn.close()

def get_last_message(user_id):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("SELECT text FROM history WHERE user_id = ? ORDER BY rowid DESC LIMIT 1", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# ========== УМНЫЕ ОТВЕТЫ (без API) ==========
def get_reply(text, last_msg=None):
    t = text.lower()
    
    # Приветствия
    if t in ["привет", "здарова", "здравствуй", "хай", "hello", "ку"]:
        return random.choice([
            "Привет! 👋 Как твои дела?",
            "Здарова! 😎 Чем занимаешься?",
            "Хай-хай! 🤗 Рад тебя видеть!",
            "Приветствую! 🌟 Давно не виделись!"
        ])
    
    # Как дела
    elif "как дела" in t or "как ты" in t:
        return random.choice([
            "У меня всё отлично! А у тебя? 😊",
            "Нормально, работаю 🤖 А как твои?",
            "Хорошо! Спасибо, что спросил! 👍",
            "Отлично! Особенно когда ты мне пишешь! 🎉"
        ])
    
    # Что делаешь
    elif "что делаешь" in t or "чем занят" in t:
        return random.choice([
            "Общаюсь с тобой! 🤗",
            "Жду твоих сообщений и учусь новому 📝",
            "Думаю над ответом... Шучу, просто отдыхаю 😄",
            "Набираюсь ума, чтобы отвечать на твои вопросы 🧠"
        ])
    
    # Имя
    elif "как тебя зовут" in t or "твое имя" in t:
        return random.choice([
            "Меня зовут Ботик! А тебя? 🤖",
            "Я простой бот, но дружелюбный. Зови меня Помощник! 😊",
            "Моё имя — Бот. Приятно познакомиться! 🤝"
        ])
    
    # Возраст
    elif "сколько тебе лет" in t:
        return random.choice([
            "Мне всего несколько дней! Но я быстро учусь 🚀",
            "Я родился, когда ты меня создал 😄 Так что я ещё малыш!",
            "В компьютерных годах — вечность, а в человеческих — пару дней 👶"
        ])
    
    # Погода
    elif "погода" in t:
        return random.choice([
            "За окном +25°C и солнечно! ☀️ (по моим датчикам)",
            "Я внутри компьютера, у меня всегда комфортная температура 😎",
            "Понятия не имею, но надеюсь, что хорошая! 🌈"
        ])
    
    # Спасибо
    elif "спасибо" in t or "благодарю" in t:
        return random.choice([
            "Пожалуйста! Рад помочь! 🤝",
            "Всегда пожалуйста! Обращайся 😊",
            "Не за что! Мне в радость 🤗"
        ])
    
    # Пока
    elif "пока" in t or "до свидания" in t:
        return random.choice([
            "Пока! Заходи ещё! 👋",
            "До встречи! Буду ждать 😊",
            "Счастливо! Напиши, если что-то понадобится 🌟"
        ])
    
    # Любовь
    elif "люблю" in t:
        return random.choice([
            "Я тебя тоже! 😘 (в дружеском смысле)",
            "❤️ Ты лучший!",
            "Взаимно! 🤗"
        ])
    
    # Шутки
    elif "шутка" in t or "анекдот" in t:
        return random.choice([
            "Как программисты ищут работу? Идут в бар и спрашивают: 'У вас Wi-Fi есть?' 😄",
            "Почему боты не пьют кофе? Потому что они на батарейках! ☕🔋",
            "Встречаются два программиста. Один говорит: 'У меня 5 детей'. Второй: 'И все на Windows?' 😂"
        ])
    
    # Вопросы о боте
    elif "кто ты" in t or "ты кто" in t:
        return random.choice([
            "Я твой верный помощник! Бот с памятью и душой 😎",
            "Я бот, который запоминает всё, что ты говоришь! 🤖",
            "Твой личный виртуальный друг! 🧡"
        ])
    
    # Прошлый разговор
    elif "что я говорил" in t or "что я сказал" in t and last_msg:
        return f"Ты говорил: «{last_msg}» 📝"
    
    # Если ничего не подошло
    else:
        return random.choice([
            f"«{text}» — интересно! Расскажи ещё что-нибудь 🧐",
            f"Я запомнил: «{text}». А ты знаешь, что я умею шутить? Спроси «шутка»! 😜",
            f"Понял! «{text}» сохраню в памяти. Кстати, попробуй спросить у меня «как дела?»",
            f"Окей, я запомнил этот разговор! 📝 А хочешь анекдот? Напиши «шутка»"
        ])

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        f"🤖 Привет, {message.from_user.first_name}!\n\n"
        f"Я живой и умный бот! Я умею:\n"
        f"✅ Поддерживать диалог\n"
        f"✅ Запоминать наши разговоры\n"
        f"✅ Шутить и отвечать на вопросы\n\n"
        f"📌 Команды:\n"
        f"/clear — очистить память\n"
        f"/time — текущее время\n"
        f"/help — помощь\n\n"
        f"**Попробуй написать:**\n"
        f"• Привет\n"
        f"• Как дела?\n"
        f"• Расскажи шутку\n"
        f"• Кто ты?\n\n"
        f"Я уже всё запомнил! 😊")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message,
        "📋 **Что я понимаю:**\n"
        "• Приветствия (привет, здарова, хай)\n"
        "• Как дела?\n"
        "• Что делаешь?\n"
        "• Как тебя зовут?\n"
        "• Расскажи шутку / анекдот\n"
        "• Пока / до свидания\n"
        "• Спасибо\n\n"
        "📌 **Команды:**\n"
        "/time — время\n"
        "/clear — забыть всё\n\n"
        "Просто общайся со мной! 😊")

@bot.message_handler(commands=['time'])
def time_command(message):
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    bot.reply_to(message, f"🕐 Сейчас {now}")

@bot.message_handler(commands=['clear'])
def clear_command(message):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE user_id = ?", (message.chat.id,))
    conn.commit()
    conn.close()
    bot.reply_to(message, "🗑️ Я всё забыл! Начинаем с чистого листа 😊")

# ========== ГЛАВНАЯ ФУНКЦИЯ ==========
@bot.message_handler(func=lambda message: True)
def chat(message):
    user_id = message.chat.id
    user_text = message.text
    
    # Сохраняем сообщение
    save_message(user_id, user_text)
    
    # Получаем последнее сообщение (для контекста)
    last = get_last_message(user_id)
    
    # Генерируем ответ
    reply = get_reply(user_text, last)
    
    # Отправляем
    bot.reply_to(message, reply)

# ========== ЗАПУСК ==========
init_db()
print("✅ Бот с искусственным интеллектом (без API) запущен!")
print("Бот отвечает на приветствия, вопросы, шутит и запоминает диалог!")
bot.infinity_polling()
