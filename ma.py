import telebot
from telebot import types
import sqlite3
import re
from datetime import datetime
import os  # ← TOKENni xavfsiz olish uchun

# Tokenni Environment Variable orqali olamiz
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 8080039848

bot = telebot.TeleBot(TOKEN)

# DATABASE
conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
phone TEXT,
subject TEXT,
time TEXT
)
""")

conn.commit()

user_data = {}

# START
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Roʻyhatdan oʻtish")
    markup.add("Bogʻlanish", "Markaz haqida")
    bot.send_message(
        message.chat.id,
        f"Assalomu alaykum {name}!\nFuture education o‘quv markazimizga xush kelibsiz!\n\nXizmatni tanlang:",
        reply_markup=markup
    )

# RO'YXATDAN O'TISH
@bot.message_handler(func=lambda m: m.text == "Roʻyhatdan oʻtish")
def register(message):
    msg = bot.send_message(
        message.chat.id,
        "Ism familiya va sinf kiriting.\n\nNamuna:\nValiyev Shahram 7-sinf"
    )
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    pattern = r"^[A-Za-zʻʼ' ]+ \d+-sinf$"
    if not re.match(pattern, message.text):
        msg = bot.send_message(
            message.chat.id,
            "❗Format noto‘g‘ri.\n\nNamuna:\nValiyev Shahram 7-sinf"
        )
        bot.register_next_step_handler(msg, get_name)
        return
    user_data[message.chat.id] = {"name": message.text}
    msg = bot.send_message(
        message.chat.id,
        "Telefon raqamingizni kiriting.\n\nNamuna:\n+998930570448"
    )
    bot.register_next_step_handler(msg, get_phone)

def get_phone(message):
    pattern = r"^\+998\d{9}$"
    if not re.match(pattern, message.text):
        msg = bot.send_message(
            message.chat.id,
            "❗Telefon format noto‘g‘ri.\n\nNamuna:\n+998930570448"
        )
        bot.register_next_step_handler(msg, get_phone)
        return
    user_data[message.chat.id]["phone"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Matematika", "Ingliz tili")
    markup.add("Majburiy matematika", "Prezident maktabi")
    msg = bot.send_message(
        message.chat.id,
        "Fan tanlang:",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, get_subject)

def get_subject(message):
    subject = message.text
    data = user_data[message.chat.id]
    time = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO students(name,phone,subject,time) VALUES(?,?,?,?)",
        (data["name"], data["phone"], subject, time)
    )
    conn.commit()
    admin_text = f"""
🎓 Yangi o‘quvchi ro‘yxatdan o‘tdi

👤 {data['name']}
📞 {data['phone']}
📚 {subject}
🕒 {time}
"""
    bot.send_message(ADMIN_ID, admin_text)
    bot.send_message(
        message.chat.id,
        "Bizni tanlaganingiz uchun rahmat!\nTez orada administratsiyamiz siz bilan bog‘lanadi."
    )

# BOGLANISH
@bot.message_handler(func=lambda m: m.text == "Bogʻlanish")
def contact(message):
    text = (
        "✈️ Telegram: @Future_admin3\n"
        "📞 +998930570449"
    )
    bot.send_message(message.chat.id,text)

# MARKAZ HAQIDA
@bot.message_handler(func=lambda m: m.text == "Markaz haqida")
def about(message):
    text = (
        "Future Education o‘quv markazi.\n"
        "Matematika, Ingliz tili va Prezident maktabiga tayyorlov kurslari mavjud."
    )
    bot.send_message(message.chat.id,text)

bot.infinity_polling()