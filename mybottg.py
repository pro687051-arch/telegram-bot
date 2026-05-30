import telebot
import requests
import sqlite3
import os
from datetime import datetime

# БЕРЁМ ТОКЕНЫ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ (важно для Render)
TELEGRAM_TOKEN = os.environ.get("8532318798:AAHaKxRHgstALFaY5ZBYKVu9Gtl0GT0yoCk")
AI_API_KEY = os.environ.get("sk-c0979d4293424f08a7ba9ffef75b98b4")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# База данных
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

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот на сервере и работаю 24/7! 🚀")

@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    user_id = message.chat.id
    save_message(user_id, "user", message.text)
    
    history = get_history(user_id, 10)
    messages = [{"role": role, "content": content} for role, content in history]
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": messages, "max_tokens": 500},
            timeout=30
        )
        if response.status_code == 200:
            ai_response = response.json()["choices"][0]["message"]["content"]
            save_message(user_id, "assistant", ai_response)
            bot.reply_to(message, ai_response)
        else:
            bot.reply_to(message, "Ошибка API")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

init_db()
print("✅ Бот запущен на сервере!")
bot.infinity_polling()