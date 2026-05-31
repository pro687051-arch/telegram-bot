import telebot
import requests
import sqlite3
from datetime import datetime

# 🔑 ТВОИ КЛЮЧИ - ЗАМЕНИ НА СВОИ!
TELEGRAM_TOKEN = "8670467955:AAE-IPPIMaagq2AYEy-EF8QDYoZZur8brFE"
DEEPSEEK_API_KEY = "sk-df155ec7805c47b7a362649d809dff67"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (user_id INTEGER, role TEXT, content TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_message(user_id, role, content):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (user_id, role, content, datetime.now()))
    conn.commit()
    conn.close()

def get_history(user_id, limit=10):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
              (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))

def clear_history(user_id):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# ========== DEEPSEEK API ==========
def ask_deepseek(question, context=""):
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты дружелюбный помощник. Отвечай кратко (2-3 предложения) и по делу."},
            {"role": "user", "content": f"Контекст разговора:\n{context}\n\nВопрос: {question}"}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            print(f"DeepSeek error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"🤖 Привет, {message.from_user.first_name}! Я бот с ИИ DeepSeek! Задавай любые вопросы!")

@bot.message_handler(commands=['clear'])
def clear_command(message):
    clear_history(message.chat.id)
    bot.reply_to(message, "🗑️ Память очищена!")

# ========== ОТВЕТ НА ЛЮБЫЕ СООБЩЕНИЯ ==========
@bot.message_handler(func=lambda message: True)
def ai_reply(message):
    user_id = message.chat.id
    user_text = message.text
    
    bot.send_chat_action(user_id, 'typing')
    save_message(user_id, "user", user_text)
    
    # Получаем контекст
    history = get_history(user_id, 5)
    context = ""
    for role, content in history[:-1]:
        context += f"{'Пользователь' if role == 'user' else 'Бот'}: {content}\n"
    
    # Спрашиваем DeepSeek
    reply = ask_deepseek(user_text, context)
    
    if not reply:
        reply = "❌ Ошибка. Попробуй ещё раз."
    
    save_message(user_id, "assistant", reply)
    bot.reply_to(message, reply)

# ========== ЗАПУСК ==========
init_db()
print("✅ Бот с DeepSeek запущен!")
bot.infinity_polling()
