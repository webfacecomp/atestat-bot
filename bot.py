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
    rus = types.KeyboardButton("Rus 🇷🇺")
    uzb = types.KeyboardButton("Uzb 🇺🇿")
    markup.add(rus, uzb)

    bot.send_message(
        message.chat.id,
        "Assalomu alaykum!\nSiz qaysi tilda suhbatlashishni hohlaysiz?",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text in ["Rus 🇷🇺", "Uzb 🇺🇿"])
def choose_lang(message):
    chat_id = message.chat.id

    if message.text == "Rus 🇷🇺":
        user_lang[chat_id] = "ru"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        teacher = types.KeyboardButton("Учитель 👨‍🏫")
        student = types.KeyboardButton("Ученик 👨‍🎓")
        markup.add(teacher, student)

        bot.send_message(chat_id, "Вы выбрали русский язык.", reply_markup=markup)
        bot.send_message(chat_id, "Вы учитель или ученик?")

    else:
        user_lang[chat_id] = "uz"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        teacher = types.KeyboardButton("O‘qituvchi 👨‍🏫")
        student = types.KeyboardButton("O‘quvchi 👨‍🎓")
        markup.add(teacher, student)

        bot.send_message(chat_id, "Siz o‘zbek tilini tanladingiz.", reply_markup=markup)
        bot.send_message(chat_id, "Siz o‘qituvchimisiz yoki o‘quvchi?")

@bot.message_handler(func=lambda m: m.text in [
    "Учитель 👨‍🏫", "Ученик 👨‍🎓",
    "O‘qituvchi 👨‍🏫", "O‘quvchi 👨‍🎓"
])
def role_chosen(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    # Keyingi menyu
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if lang == "ru":
        schedule = types.KeyboardButton("Расписание уроков 🗓")
        chsb = types.KeyboardButton("ЧСБ демо ⚙️")
        iq = types.KeyboardButton("IQ вопросы 🧠")
        test = types.KeyboardButton("Предметные тесты 📘")
        markup.add(schedule, chsb, iq, test)

        bot.send_message(chat_id, "Чем могу помочь?", reply_markup=markup)

    else:
        schedule = types.KeyboardButton("Dars jadvali 🗓")
        chsb = types.KeyboardButton("ChSB demo ⚙️")
        iq = types.KeyboardButton("IQ savollar 🧠")
        test = types.KeyboardButton("Fan testlari 📘")
        markup.add(schedule, chsb, iq, test)

        bot.send_message(chat_id, "Mendan sizga qanday yordam kerak?", reply_markup=markup)

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
