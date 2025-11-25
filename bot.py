import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Har bir userning tili, roli, sinfi va guruhini saqlash uchun
user_lang = {}
user_stage = {}
user_class = {}

# ================================
# /start – TIL TANLASH
# ================================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("Rus 🇷🇺"),
        types.KeyboardButton("Uzb 🇺🇿")
    )
    bot.send_message(
        message.chat.id,
        "Assalomu alaykum!\nSiz qaysi tilda suhbatlashishni xohlaysiz?",
        reply_markup=markup
    )


# ================================
# TIL TANLANGANDA ROLE SAVOLI
# ================================
@bot.message_handler(func=lambda m: m.text in ["Rus 🇷🇺", "Uzb 🇺🇿"])
def choose_lang(message):
    chat_id = message.chat.id

    if message.text == "Rus 🇷🇺":
        user_lang[chat_id] = "ru"
        msg = "Вы выбрали русский язык."
        role_text = "Вы учитель или ученик?"
        teacher = "Учитель 👨🏻‍🏫"
        student = "Ученик 🧑🏻‍🎓"

    else:
        user_lang[chat_id] = "uz"
        msg = "Siz o‘zbek tilini tanladingiz."
        role_text = "Siz o‘qituvchimisiz yoki o‘quvchi?"
        teacher = "O‘qituvchi 👨🏻‍🏫"
        student = "O‘quvchi 🧑🏻‍🎓"

    bot.send_message(chat_id, msg)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(teacher), types.KeyboardButton(student))

    bot.send_message(chat_id, role_text, reply_markup=markup)


# ================================
# ROLE TANLANGANDA — ASOSIY MENYU
# ================================
@bot.message_handler(func=lambda m: m.text in [
    "Учитель 👨🏻‍🏫", "Ученик 🧑🏻‍🎓",
    "O‘qituvchi 👨🏻‍🏫", "O‘quvchi 🧑🏻‍🎓"
])
def role_chosen(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if lang == "ru":
        bot.send_message(chat_id, "Как я могу помочь вам?")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Расписание уроков 📑", "ЧСБ демо 📝", "IQ вопросы 🧠", "Тесты по предметам 🔖")
    else:
        bot.send_message(chat_id, "Menga sizga qanday yordam kerak?")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Dars jadvali 📑", "ChSB demo 📝", "IQ savollar 🧠", "Fan testlari 🔖")

    bot.send_message(chat_id, "Quyidagilardan birini tanlang:", reply_markup=markup)


# ================================
# DARS JADVALI – 1-QADAM (SINF TANLASH)
# ================================
@bot.message_handler(func=lambda m: m.text in ["Dars jadvali 📑", "Расписание уроков 📑"])
def ask_class(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    user_stage[chat_id] = "choose_class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    classes = ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]
    for c in classes:
        markup.add(c)

    text = "Выберите класс:" if lang == "ru" else "Siz nechinchi sinfsiz?"
    bot.send_message(chat_id, text, reply_markup=markup)


# ================================
# GURUHLAR RO‘YXATI
# ================================
groups = {
    "5": ["5-01", "5-02"],
    "6": ["6-01", "6-02"],
    "7": ["7-01", "7-02", "7-03"],
    "8": ["8-01", "8-02", "8-03"],
    "9": ["9-01", "9-02", "9-03"],
    "10": ["10-01", "10-02", "10-03"],
    "11": ["11-01", "11-02", "11-03"],
}


# ================================
# SINF TANLANGANDA — GURUH TANLASH
# ================================
@bot.message_handler(func=lambda m: m.text in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"])
def choose_group(message):
    chat_id = message.chat.id
    sinf = message.text.replace("-sinf", "")
    user_class[chat_id] = sinf
    user_stage[chat_id] = "choose_group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[sinf]:
        markup.add(g)

    lang = user_lang.get(chat_id, "uz")
    text = "Выберите группу:" if lang == "ru" else "Siz qaysi guruhsiz?"
    bot.send_message(chat_id, text, reply_markup=markup)


# ================================
# RASM YUBORISH
# ================================
@bot.message_handler(func=lambda m: m.text in sum(groups.values(), []))
def send_schedule(message):
    chat_id = message.chat.id
    group = message.text
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(base_dir, "images", f"{group}.jpg")

    try:
        with open(image_path, "rb") as img:
            bot.send_photo(chat_id, img, caption=f"{group} dars jadvali 📚")
    except FileNotFoundError:
        bot.send_message(chat_id, "Dars jadvali mavjud emas.")


# ================================
# CALLBACK EXAMPLE – /callback
# ================================
@bot.message_handler(commands=['callback'])
def send_test(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="Etiroz yuborish ✍🏼",
        callback_data="test_clicked"
    )
    keyboard.add(btn)

    bot.send_message(message.chat.id, "Agar bot haqida etirozlaringiz bolsa pastni bosing 👇🏼."
    "Men tez orada sizga javob qaytaraman!", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "test_clicked")
def callback_handler(call):
    bot.answer_callback_query(call.id)
    my_telegram_id = 6894161022  # O'zingizning shaxsiy Telegram ID
    bot.send_message(my_telegram_id, f"Foydalanuvchi @{call.from_user.username} callback tugmasini bosdi!")


# ================================
# BOTNI ISHGA TUSHIRISH
# ================================
bot.infinity_polling()
