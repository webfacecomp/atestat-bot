import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

groups = {
    "5": ["5-01", "5-02"],
    "6": ["6-01", "6-02"],
    "7": ["7-01", "7-02", "7-03"],
    "8": ["8-01", "8-02", "8-03"],
    "9": ["9-01", "9-02", "9-03"],
    "10": ["10-01", "10-02"],
    "11": ["11-01", "11-02"]
}

user_stage = {}
user_class = {}

# =====================================================
# ASOSIY MENU
# =====================================================

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📚 Dars jadvali")
    markup.add("✍🏼 Feedback")
    return markup

# =====================================================
# START
# =====================================================

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Xush kelibsiz! Kerakli bo‘limni tanlang:",
        reply_markup=main_menu()
    )

# =====================================================
# DARS JADVALI BOSILSA
# =====================================================

@bot.message_handler(func=lambda m: m.text == "📚 Dars jadvali")
def ask_class(message):
    user_stage[message.chat.id] = "class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(5, 12):
        markup.add(f"{i}-sinf")
    markup.add("🔙 Orqaga")

    bot.send_message(message.chat.id, "Sinfni tanlang:", reply_markup=markup)

# =====================================================
# SINFDAN KEYIN GURUH
# =====================================================

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "class")
def choose_group(message):
    if message.text == "🔙 Orqaga":
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu())
        user_stage.pop(message.chat.id, None)
        return

    sinf = message.text.replace("-sinf", "")
    if sinf not in groups:
        return

    user_class[message.chat.id] = sinf
    user_stage[message.chat.id] = "group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[sinf]:
        markup.add(g)
    markup.add("🔙 Orqaga")

    bot.send_message(message.chat.id, "Guruhni tanlang:", reply_markup=markup)

# =====================================================
# GURUH TANLANGANDA
# =====================================================

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "group")
def send_schedule(message):
    if message.text == "🔙 Orqaga":
        ask_class(message)
        return

    group = message.text
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(BASE_DIR, "images", f"{group}.jpg")

    try:
        with open(path, "rb") as img:
            bot.send_photo(message.chat.id, img, caption=f"{group} dars jadvali 📚")
    except:
        bot.send_message(message.chat.id, "Dars jadvali topilmadi.")

    bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu())
    user_stage.pop(message.chat.id, None)

# =====================================================
# FEEDBACK
# =====================================================

def get_feedback_inline():
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="E'tiroz yuborish ✍🏼",
        url="https://t.me/khakimovvd"
    )
    keyboard.add(btn)
    return keyboard

@bot.message_handler(func=lambda m: m.text == "✍🏼 Feedback")
def feedback(message):
    bot.send_message(
        message.chat.id,
        "Taklif yoki e’tiroz yuborish uchun pastdagi tugmani bosing:",
        reply_markup=get_feedback_inline()
    )

# =====================================================
# BOT START
# =====================================================

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling()