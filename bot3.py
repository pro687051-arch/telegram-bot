import telebot
import requests
import sqlite3
from datetime import datetime

# 🔑 ТВОИ КЛЮЧИ
TELEGRAM_TOKEN = "8670467955:AAE-IPPIMaagq2AYEy-EF8QDYoZZur8brFE"
DEEPSEEK_API_KEY = "sk-540d6f9dc8a24521b6ce6dbcee6a9ffe"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ========== БАЗА ДАННЫХ (память) ==========
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

# ========== ПОЛУЧЕНИЕ ОТВЕТА ОТ DEEPSEEK ==========
def ask_deepseek(question, context=""):
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    full_prompt = f"""Ты дружелюбный помощник. Отвечай кратко (максимум 2-3 предложения) и по делу.
    
Контекст разговора:
{context}

Вопрос: {question}
Ответ:"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты дружелюбный помощник. Отвечай кратко и по делу."},
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
            print(f"DeepSeek error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"DeepSeek exception: {e}")
        return None

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        f"🤖 Привет, {message.from_user.first_name}!\n\n"
        f"Я **умный бот с ИИ DeepSeek**! 🧠\n\n"
        f"📌 **Что я умею:**\n"
        f"• Отвечать на **любые вопросы**\n"
        f"• Запоминать **наши диалоги**\n"
        f"• Понимать **контекст** разговора\n\n"
        f"📌 **Команды:**\n"
        f"/clear - очистить память\n"
        f"/help - помощь\n\n"
        f"**Попробуй спросить меня о чём угодно!** 👇")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message,
        "🧠 **Я умный бот с искусственным интеллектом DeepSeek!**\n\n"
        "Ты можешь спросить меня:\n"
        "• О чём угодно\n"
        "• Я понимаю контекст\n"
        "• Запоминаю разговор\n\n"
        "📌 **Команды:**\n"
        "/clear - забыть наш разговор\n"
        "/start - начать заново\n\n"
        "Просто напиши вопрос!")

@bot.message_handler(commands=['clear'])
def clear_command(message):
    clear_history(message.chat.id)
    bot.reply_to(message, "🗑️ Я всё забыл! Начинаем чистый диалог.")

# ========== ОТВЕТ НА ЛЮБОЕ СООБЩЕНИЕ ==========
@bot.message_handler(func=lambda message: True)
def ai_reply(message):
    user_id = message.chat.id
    user_text = message.text
    
    # Показываем, что бот печатает
    bot.send_chat_action(user_id, 'typing')
    
    # Сохраняем вопрос пользователя
    save_message(user_id, "user", user_text)
    
    # Получаем историю для контекста
    history = get_history(user_id, 5)
    context = ""
    for role, content in history[:-1]:  # всё кроме последнего сообщения
        if role == "user":
            context += f"Пользователь: {content}\n"
        else:
            context += f"Бот: {content}\n"
    
    # Спрашиваем у DeepSeek
    reply = ask_deepseek(user_text, context)
    
    # Если DeepSeek не ответил (ошибка), используем запасные ответы
    if not reply:
        reply = "❌ Не могу ответить. Попробуй перефразировать вопрос или напиши /start"
    
    # Сохраняем ответ
    save_message(user_id, "assistant", reply)
    
    # Отправляем ответ
    bot.reply_to(message, reply)

# ========== ЗАПУСК ==========
init_db()
print("✅ Умный бот с DeepSeek запущен!")
print("Бот отвечает на любые вопросы и помнит диалог!")
bot.infinity_polling()