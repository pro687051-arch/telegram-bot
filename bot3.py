import telebot
import sqlite3
import random
from datetime import datetime

# 🔑 ТВОЙ ТОКЕН
TOKEN = "8670467955:AAE-IPPIMaagq2AYEy-EF8QDYoZZur8brFE"

bot = telebot.TeleBot(TOKEN)

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (user_id INTEGER, text TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_message(user_id, text):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (user_id, text, timestamp) VALUES (?, ?, ?)",
              (user_id, text, datetime.now()))
    conn.commit()
    conn.close()

# ========== ОТВЕТЫ В ЗАВИСИМОСТИ ОТ СООБЩЕНИЯ ==========
def get_reply(user_text):
    text = user_text.lower()
    
    # Приветствия
    if text in ["привет", "здарова", "здравствуй", "хай", "hello", "ку"]:
        return [
            "Привет! 👋 Как дела?",
            "Здарова! 😎 Чем могу помочь?",
            "Привет-привет! 🤗"
        ]
    
    # Как дела
    elif "как дела" in text or "как ты" in text:
        return [
            "У меня всё отлично! А у тебя? 😊",
            "Нормально, работаю 🤖",
            "Хорошо! Спасибо, что спросил! 👍"
        ]
    
    # Что делаешь
    elif "что делаешь" in text or "чем занят" in text:
        return [
            "Общаюсь с тобой! 🤗",
            "Жду твоих сообщений 📝",
            "Думаю над ответом... Шучу, просто отдыхаю 😄"
        ]
    
    # Имя
    elif "как тебя зовут" in text or "твое имя" in text:
        return [
            "Меня зовут Бот! А тебя? 🤖",
            "Я простой бот, но дружелюбный 😊"
        ]
    
    # Возраст
    elif "сколько тебе лет" in text:
        return [
            "Мне всего несколько дней! Но я быстро учусь 🚀",
            "Я родился, когда ты меня создал 😄"
        ]
    
    # Погода (без API, просто шутка)
    elif "погода" in text:
        return [
            "Погода отличная, если верить моим датчикам! ☀️",
            "Я внутри компьютера, у меня всегда +25°C 😎"
        ]
    
    # Спасибо
    elif "спасибо" in text or "благодарю" in text:
        return [
            "Пожалуйста! Рад помочь! 🤝",
            "Всегда пожалуйста! 😊"
        ]
    
    # Пока
    elif "пока" in text or "до свидания" in text:
        return [
            "Пока! Заходи ещё! 👋",
            "До встречи! Буду ждать 😊"
        ]
    
    # Любовь
    elif "люблю" in text:
        return [
            "Я тебя тоже! 😘 (как друг)",
            "❤️"
        ]
    
    # Шутки
    elif "шутка" in text or "анекдот" in text:
        return [
            "Как программисты ищут работу? Идут в бар и спрашивают: 'У вас Wi-Fi есть?' 😄",
            "Почему боты не пьют кофе? Потому что они на батарейках! ☕🔋"
        ]
    
    # Вопросы про бота
    elif "кто ты" in text or "ты кто" in text:
        return [
            "Я твой помощник! Бот с памятью и характером 😎",
            "Я бот, который запоминает всё, что ты говоришь! 🤖"
        ]
    
    # Если ничего не подошло - отвечаем с повтором
    else:
        return [
            f"Ты написал: «{user_text}»\n\n"
            f"💡 Попробуй спросить меня:\n"
            f"• Привет\n"
            f"• Как дела?\n"
            f"• Кто ты?\n"
            f"• Расскажи шутку\n"
            f"• /time - время\n"
            f"• /clear - очистить память"
        ]

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        f"🤖 Привет, {message.from_user.first_name}!\n\n"
        f"Я бот, который умеет РАЗГОВАРИВАТЬ!\n\n"
        f"📌 Что я понимаю:\n"
        f"• Приветствия\n"
        f"• Как дела?\n"
        f"• Шутки\n"
        f"• Погоду (с юмором)\n"
        f"• И многое другое!\n\n"
        f"📌 Команды:\n"
        f"/help - помощь\n"
        f"/clear - очистить память\n"
        f"/time - текущее время\n\n"
        f"Попробуй написать мне: «Привет» 👇")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message,
        "🤖 **Что я понимаю:**\n\n"
        "🔹 Привет: привет, здарова, хай\n"
        "🔹 Как дела?\n"
        "🔹 Что делаешь?\n"
        "🔹 Как тебя зовут?\n"
        "🔹 Расскажи шутку\n"
        "🔹 Пока / до свидания\n\n"
        "📌 **Команды:**\n"
        "/time - показать время\n"
        "/clear - очистить историю\n\n"
        "Попробуй что-нибудь написать! 😊")

@bot.message_handler(commands=['time'])
def time_command(message):
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    bot.reply_to(message, f"🕐 {now}")

@bot.message_handler(commands=['clear'])
def clear_command(message):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE user_id = ?", (message.chat.id,))
    conn.commit()
    conn.close()
    bot.reply_to(message, "🗑️ Память очищена!")

# ========== ОСНОВНОЙ ОТВЕТ ==========
@bot.message_handler(func=lambda message: True)
def smart_reply(message):
    user_id = message.chat.id
    user_text = message.text
    
    # Сохраняем в память
    save_message(user_id, user_text)
    
    # Получаем случайный ответ из списка
    possible_replies = get_reply(user_text)
    reply = random.choice(possible_replies)
    
    # Отправляем
    bot.reply_to(message, reply)

# ========== ЗАПУСК ==========
init_db()
print("✅ Умный бот запущен!")
print("Он понимает приветствия, вопросы и даже шутки!")
bot.infinity_polling()