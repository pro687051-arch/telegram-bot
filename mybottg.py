import telebot
import sqlite3
import re
from datetime import datetime

TELEGRAM_TOKEN = "8532318798:AAHaKxRHgstALFaY5ZBYKVu9Gtl0GT0yoCk"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ========== БАЗА ДАННЫХ (память) ==========
def init_db():
    conn = sqlite3.connect('bot_memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (user_id INTEGER, role TEXT, content TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_message(user_id, role, content):
    conn = sqlite3.connect('bot_memory.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (user_id, role, content, datetime.now()))
    conn.commit()
    conn.close()

def get_history(user_id, limit=10):
    conn = sqlite3.connect('bot_memory.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
              (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))

def clear_history(user_id):
    conn = sqlite3.connect('bot_memory.db')
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# ========== ИНСТРУМЕНТЫ ==========
def get_current_time():
    now = datetime.now()
    return f"🕐 Сегодня {now.strftime('%d.%m.%Y')}, время {now.strftime('%H:%M:%S')}"

def calculate(expression):
    try:
        # Разрешены только цифры и базовые операции
        if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expression):
            result = eval(expression)
            return f"📊 Результат: {result}"
        else:
            return "❌ Можно использовать только цифры и операции + - * / ( )"
    except:
        return "❌ Не могу вычислить. Пример: 25*4 или (10+5)/3"

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    bot.reply_to(message,
        f"🤖 Привет, {user.first_name}!\n\n"
        f"Я бот с памятью. Я помню, что ты мне говорил!\n\n"
        f"📌 Команды:\n"
        f"/help - все команды\n"
        f"/clear - очистить память\n"
        f"/time - текущее время\n"
        f"/calc 2+2 - посчитать\n\n"
        f"Просто напиши мне что-нибудь!")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message,
        "📋 **Мои команды:**\n\n"
        "/start - приветствие\n"
        "/help - эта справка\n"
        "/clear - очистить историю диалога\n"
        "/time - показать время и дату\n"
        "/calc 2+2*3 - вычислить пример\n\n"
        "💾 Я запоминаю наши диалоги!\n"
        "Напиши что-нибудь, и я отвечу с учётом контекста.")

@bot.message_handler(commands=['time'])
def time_command(message):
    bot.reply_to(message, get_current_time())

@bot.message_handler(commands=['calc'])
def calc_command(message):
    expr = message.text.replace('/calc', '').strip()
    if expr:
        bot.reply_to(message, calculate(expr))
    else:
        bot.reply_to(message, "Напиши пример: /calc 15*8")

@bot.message_handler(commands=['clear'])
def clear_command(message):
    clear_history(message.chat.id)
    bot.reply_to(message, "🗑️ История диалогов очищена!")

# ========== ОБРАБОТКА ОБЫЧНЫХ СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def chat_with_memory(message):
    user_id = message.chat.id
    user_text = message.text
    
    # Сохраняем сообщение пользователя
    save_message(user_id, "user", user_text)
    
    # Получаем историю последних сообщений
    history = get_history(user_id, 5)
    
    # Если есть история, отвечаем с учётом контекста
    if len(history) > 1:
        # Находим последний вопрос-ответ
        context = ""
        for role, content in history[-3:]:
            if role == "user":
                context += f"Ты сказал: {content}\n"
            else:
                context += f"Я ответил: {content}\n"
        
        # Простые ответы с памятью
        last_user_msg = history[-1][1] if history else ""
        
        if "привет" in user_text.lower() or "здарова" in user_text.lower():
            reply = "Привет! Рад тебя снова видеть! 👋"
        elif "как дела" in user_text.lower():
            reply = "У меня всё отлично! А у тебя? 😊"
        elif "что я говорил" in user_text.lower() or "что я сказал" in user_text.lower():
            if len(history) > 1:
                prev_msg = history[-2][1] if len(history) > 1 else "ничего"
                reply = f"Ты говорил: «{prev_msg}»"
            else:
                reply = "Ты ещё ничего не говорил."
        elif "спасибо" in user_text.lower():
            reply = "Пожалуйста! Всегда рад помочь 🤝"
        elif "пока" in user_text.lower():
            reply = "До свидания! Заходи ещё! 👋"
        else:
            reply = f"Я помню наш разговор! Ты написал: «{user_text}»\n\n💡 Попробуй спросить что-то конкретное или используй /help"
    else:
        # Если история пустая или короткая
        reply = f"Я тебя услышал: «{user_text}»\n\n📌 Напиши /help, чтобы узнать, что я умею."
    
    # Сохраняем ответ бота
    save_message(user_id, "assistant", reply)
    
    # Отправляем ответ
    bot.reply_to(message, reply)

# ========== ЗАПУСК ==========
init_db()
print("✅ Бот с памятью запущен!")
print("📌 Команды: /start, /help, /clear, /time, /calc")
bot.infinity_polling()
