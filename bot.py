import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_lang = {}       # chat_id → "uz" yoki "ru"
user_grade = {}      # chat_id → "5"
user_parallel = {}   # chat_id → "5-01"

# -------------------- START -----------------------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("Uzb 🇺🇿"),
        types.KeyboardButton("Rus 🇷🇺")
    )
    bot.send_message(
        message.chat.id,
        "Assalomu alaykum! / Привет!\nTilni tanlang / Выберите язык:",
        reply_markup=markup
    )


@bot.message_handler(commands=['callback'])
def send(message):
    send mess="Etirozlaringiz bolsa menga murojat qiling! @khakimovvd"

# -------------------- TIL TANLASH -----------------------------
@bot.message_handler(func=lambda m: m.text in ["Uzb 🇺🇿", "Rus 🇷🇺"])
def choose_lang(message):
    chat_id = message.chat.id

    if message.text == "Uzb 🇺🇿":
        user_lang[chat_id] = "uz"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("O‘qituvchi 👨🏻‍🏫", "O‘quvchi 🧑🏻‍🎓")
        bot.send_message(chat_id, "Siz o‘qituvchimisiz yoki o‘quvchi?", reply_markup=markup)

    else:
        user_lang[chat_id] = "ru"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Учитель 👨🏻‍🏫", "Ученик 🧑🏻‍🎓")
        bot.send_message(chat_id, "Вы учитель или ученик?", reply_markup=markup)

# -------------------- ROL TANLASH -----------------------------
@bot.message_handler(func=lambda m: m.text in [
    "O‘qituvchi 👨🏻‍🏫", "O‘quvchi 🧑🏻‍🎓",
    "Учитель 👨🏻‍🏫", "Ученик 🧑🏻‍🎓"
])
def role_chosen(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if lang == "uz":
        markup.add("Dars jadvali 🗓")
        markup.add("ChSB demo 📑")
        markup.add("IQ savollar 🧠")
        markup.add("Fan testlari 📘")
        bot.send_message(chat_id, "Mendan sizga qanday yordam kerak?", reply_markup=markup)

    else:
        markup.add("Расписание уроков 🗓")
        markup.add("ЧСБ демо 📑")
        markup.add("IQ вопросы 🧠")
        markup.add("Предметные тесты 📘")
        bot.send_message(chat_id, "Чем могу помочь?", reply_markup=markup)

# -------------------- DARS JADVALI TANLASH -----------------------------
@bot.message_handler(func=lambda m: "jadval" in m.text.lower() or "расписание" in m.text.lower())
def ask_grade(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(c)

    bot.send_message(message.chat.id, "Siz nechinchi sinfsiz?", reply_markup=markup)

# -------------------- SINfni tanlash → parallel chiqarish -----------------------------
@bot.message_handler(func=lambda m: m.text in [
    "5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"
])
def choose_parallel(message):
    chat_id = message.chat.id
    grade = message.text.split("-")[0]  # "5"

    user_grade[chat_id] = grade

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    parallel_count = {
        "5": 2,
        "6": 2,
        "7": 3,
        "8": 3,
        "9": 3,
        "10": 3,
        "11": 3
    }

    for i in range(1, parallel_count[grade] + 1):
        btn = f"{grade}-0{i}"
        markup.add(btn)

    bot.send_message(chat_id, "Qaysi sinf-parallel siz?", reply_markup=markup)

# -------------------- DARS JADVALI RASM YUBORISH -----------------------------
@bot.message_handler(func=lambda m: "-" in m.text and m.text[0].isdigit())
def send_schedule(message):
    chat_id = message.chat.id
    parallel = message.text  # masalan "5-01"

    image_path = f"images/{parallel}.jpg"   # images/5-01.jpg

    print("FAYL:", image_path)

    if not os.path.exists(image_path):
        bot.send_message(chat_id, "❗ Bu sinf uchun rasm topilmadi.")
        return

    with open(image_path, "rb") as img:
        bot.send_photo(chat_id, img, caption=f"{parallel} dars jadvali 🗓")

# -------------------- START POLLING -----------------------------
bot.infinity_polling()
