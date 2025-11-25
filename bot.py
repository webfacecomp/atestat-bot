import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_lang = {}
user_role = {}

# --------------------------
#  START — Til so'rash
# --------------------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Rus 🇷🇺"), types.KeyboardButton("Uzb 🇺🇿"))

    bot.send_message(
        message.chat.id,
        "Assalomu alaykum!\nSiz qaysi tilda suhbatlashishni hohlaysiz?",
        reply_markup=markup
    )

# --------------------------
#  Til tanlandi → rol tanlash
# --------------------------
@bot.message_handler(func=lambda m: m.text in ["Rus 🇷🇺", "Uzb 🇺🇿"])
def choose_lang(message):
    chat_id = message.chat.id

    if message.text == "Rus 🇷🇺":
        user_lang[chat_id] = "ru"
        bot.send_message(chat_id, "Вы выбрали русский язык.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Учитель 👨‍🏫"), types.KeyboardButton("Ученик 👨‍🎓"))
        bot.send_message(chat_id, "Вы учитель или ученик?", reply_markup=markup)

    else:
        user_lang[chat_id] = "uz"
        bot.send_message(chat_id, "Siz o‘zbek tilini tanladingiz.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("O‘qituvchi 👨‍🏫"), types.KeyboardButton("O‘quvchi 👨‍🎓"))
        bot.send_message(chat_id, "Siz o‘qituvchimisiz yoki o‘quvchi?", reply_markup=markup)

# --------------------------
# Rol tanlandi → Asosiy menyuga o'tish
# --------------------------
@bot.message_handler(func=lambda m: m.text in [
    "Учитель 👨‍🏫", "Ученик 👨‍🎓",
    "O‘qituvchi 👨‍🏫", "O‘quvchi 👨‍🎓"
])
def role_chosen(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    user_role[chat_id] = message.text  # role saqlab qo'yiladi

    # Asosiy menyu tugmalari
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(
        types.KeyboardButton("📚 Dars jadvali"),
        types.KeyboardButton("🧠 ChSB demo"),
        types.KeyboardButton("📝 IQ savollar"),
        types.KeyboardButton("📘 Fan testlari")
    )

    if lang == "ru":
        bot.send_message(chat_id, "Чем я могу вам помочь?", reply_markup=menu)
    else:
        bot.send_message(chat_id, "Mendan sizga qanday yordam kerak?", reply_markup=menu)

# --------------------------
#  Asosiy menyu → Dars jadvali bosilganda
# --------------------------
@bot.message_handler(func=lambda m: m.text == "📚 Dars jadvali")
def ask_grade(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(5, 12):
        markup.add(types.KeyboardButton(f"{i}-sinf"))
    bot.send_message(message.chat.id, "Siz nechinchi sinfsiz?", reply_markup=markup)

# --------------------------
# Sinf tanlangandan keyin — sinf guruhlarini chiqarish
# --------------------------
@bot.message_handler(func=lambda m: m.text.endswith("-sinf"))
def choose_subclass(message):
    sinf = message.text.replace("-sinf", "")
    sinf = int(sinf)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Har bir sinfga mos guruhlar
    if sinf == 5:
        groups = ["5-01", "5-02"]
    elif sinf == 6:
        groups = ["6-01", "6-02"]
    elif sinf == 7:
        groups = ["7-01", "7-02", "7-03"]
    elif sinf == 8:
        groups = ["8-01", "8-02", "8-03"]
    elif sinf == 9:
        groups = ["9-01", "9-02", "9-03"]
    elif sinf == 10:
        groups = ["10-01", "10-02", "10-03"]
    elif sinf == 11:
        groups = ["11-01", "11-02", "11-03"]
    else:
        groups = []

    for g in groups:
        markup.add(types.KeyboardButton(g))

    bot.send_message(message.chat.id, "Siz qaysi sinfni tanlaysiz?", reply_markup=markup)

# --------------------------
# Sinf-guruh tanlangandan keyin rasm jo‘natish
# --------------------------
@bot.message_handler(func=lambda m: "-" in m.text and m.text[:2].isdigit())
def send_schedule(message):
    group = message.text  # masalan: 7-01
    image_path = f"images/{group}.jpg"

    if os.path.exists(image_path):
        with open(image_path, "rb") as img:
            bot.send_photo(message.chat.id, img, caption=f"{group} dars jadvali 📚")
    else:
        bot.send_message(message.chat.id, "Bu sinf uchun dars jadvali hali yuklanmagan.")

# --------------------------
# QOLGAN MENYU BO'LIMLARI
# --------------------------
@bot.message_handler(func=lambda m: m.text == "🧠 ChSB demo")
def chsb_demo(message):
    # TODO: Bu bo'lim keyin to'ldiriladi
    bot.send_message(message.chat.id, "ChSB demo bo‘limi tez orada qo‘shiladi 😊")

@bot.message_handler(func=lambda m: m.text == "📝 IQ savollar")
def iq_questions(message):
    # TODO: Bu yerga IQ savollar funksiyasi yoziladi
    bot.send_message(message.chat.id, "IQ savollar bo‘limi hozircha tayyor emas 😊")

@bot.message_handler(func=lambda m: m.text == "📘 Fan testlari")
def fan_tests(message):
    # TODO: Bu yerga fan testlari tizimi qo‘shiladi
    bot.send_message(message.chat.id, "Fan testlari bo‘limi tez orada ishga tushadi 😊")

# --------------------------

bot.infinity_polling()
