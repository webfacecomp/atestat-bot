import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Guruhlar
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

# ============================================================
# START → SINFLARNI CHIQARADI
# ============================================================

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_stage[chat_id] = "choose_class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(5, 12):
        markup.add(f"{i}-sinf")

    bot.send_message(chat_id, "Sinfni tanlang:", reply_markup=markup)

# ============================================================
# SINFDAN KEYIN GURUH TANLASH
# ============================================================

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "choose_class")
def choose_group(message):
    chat_id = message.chat.id
    text = message.text.replace("-sinf", "")

    if text not in groups:
        return

    user_stage[chat_id] = "choose_group"
    user_stage[str(chat_id)+"_class"] = text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[text]:
        markup.add(g)

    bot.send_message(chat_id, "Guruhni tanlang:", reply_markup=markup)

# ============================================================
# GURUH TANLANGANDA RASM YUBORADI
# ============================================================

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "choose_group")
def send_schedule(message):
    chat_id = message.chat.id
    group = message.text

    path = f"images/{group}.jpg"

    try:
        with open(path, "rb") as img:
            bot.send_photo(chat_id, img, caption=f"{group} dars jadvali 📚")
    except:
        bot.send_message(chat_id, "Dars jadvali topilmadi.")

    user_stage.pop(chat_id, None)

# ============================================================
# CALLBACK FUNKSIYASINI SAQLAYMIZ
# ============================================================

def get_feedback_inline():
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="E'tiroz yuborish ✍🏼",
        url="https://t.me/khakimovvss"
    )
    keyboard.add(btn)
    return keyboard

@bot.message_handler(commands=['feedback'])
def send_test(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "Agar bot haqida e’tirozlaringiz bo‘lsa pastdagi tugmani bosing 👇🏼",
        reply_markup=get_feedback_inline()
    )

# ============================================================
# BOT START
# ============================================================

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling()