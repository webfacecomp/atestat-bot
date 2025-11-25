import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# User ma’lumotlarini saqlash
user_lang = {}      # ru / uz
user_role = {}      # student / teacher
user_stage = {}     # qaysi bosqichda
user_class = {}     # sinf

# ============================================
# /start — TIL TANLASH
# ============================================
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Rus 🇷🇺", "Uzb 🇺🇿")

    bot.send_message(
        chat_id,
        "Assalomu alaykum!\nSiz qaysi tilda suhbatlashishni xohlaysiz?",
        reply_markup=markup
    )


# ============================================
# TIL TANLANGANDA — ROLE SAVOLI
# ============================================
@bot.message_handler(func=lambda m: m.text in ["Rus 🇷🇺", "Uzb 🇺🇿"])
def choose_lang(message):
    chat_id = message.chat.id
    lang = "ru" if message.text == "Rus 🇷🇺" else "uz"
    user_lang[chat_id] = lang

    if lang == "ru":
        msg = "Вы выбрали русский язык."
        ask = "Вы учитель или ученик?"
        teacher = "Учитель 👨🏻‍🏫"
        student = "Ученик 🧑🏻‍🎓"
    else:
        msg = "Siz o‘zbek tilini tanladingiz."
        ask = "Siz o‘qituvchimisiz yoki o‘quvchi?"
        teacher = "O‘qituvchi 👨🏻‍🏫"
        student = "O‘quvchi 🧑🏻‍🎓"

    bot.send_message(chat_id, msg)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(teacher, student)

    bot.send_message(chat_id, ask, reply_markup=markup)


# ============================================
# ROLE TANLANGANDA — ALOHIDA MENYULAR
# ============================================
@bot.message_handler(func=lambda m: m.text in [
    "Учитель 👨🏻‍🏫", "Ученик 🧑🏻‍🎓",
    "O‘qituvchi 👨🏻‍🏫", "O‘quvchi 🧑🏻‍🎓"
])
def role_chosen(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    # O‘qituvchi
    if message.text in ["Учитель 👨🏻‍🏫", "O‘qituvchi 👨🏻‍🏫"]:
        user_role[chat_id] = "teacher"

        text = ("Пока для учителей нет функций, но скоро будут!" if lang == "ru"
                else "Hozircha o‘qituvchilar uchun funksiyalar yo‘q, tez orada qo‘shiladi!")

        bot.send_message(chat_id, text)
        return

    # O‘quvchi
    user_role[chat_id] = "student"

    if lang == "ru":
        bot.send_message(chat_id, "Как я могу помочь вам?")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            "Расписание уроков 📑",
            "ЧСБ демо 📝",
            "IQ вопросы 🧠",
            "Тесты по предметам 🔖",
            "SAT задачи 📘",
            "Я не ученик"
        )
    else:
        bot.send_message(chat_id, "Menga sizga qanday yordam kerak?")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            "Dars jadvali 📑",
            "ChSB demo 📝",
            "IQ savollar 🧠",
            "Fan testlari 🔖",
            "SAT misollari 📘",
            "Men o‘quvchi emasman"
        )

    bot.send_message(chat_id, "Quyidagilardan birini tanlang:", reply_markup=markup)


# ============================================
# “Men o‘quvchi emasman” — ROLE RESET
# ============================================
@bot.message_handler(func=lambda m: m.text in ["Men o‘quvchi emasman", "Я не ученик"])
def not_student(message):
    chat_id = message.chat.id

    lang = user_lang.get(chat_id, "uz")

    if lang == "ru":
        bot.send_message(chat_id, "Хорошо, выберите роль снова.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Учитель 👨🏻‍🏫", "Ученик 🧑🏻‍🎓")
    else:
        bot.send_message(chat_id, "Yaxshi, rolni qaytadan tanlang.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("O‘qituvchi 👨🏻‍🏫", "O‘quvchi 🧑🏻‍🎓")

    bot.send_message(chat_id, "Tanlang:", reply_markup=markup)



# ================================
# DARS JADVALI – SINF TANLASH
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



# ============================================
# UNIVERSAL — BEKOR QILISH & BOSHLANG‘ICH MENYU
# ============================================
def get_cancel_buttons(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "ru":
        markup.add("Отмена ↩️", "Главное меню ⏪")
    else:
        markup.add("Bekor qilish ↩️", "Bosh menyu ⏪")
    return markup


@bot.message_handler(func=lambda m: m.text in ["Bekor qilish ↩️", "Отмена ↩️"])
def cancel_action(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if lang == "ru":
        bot.send_message(chat_id, "Действие отменено.")
    else:
        bot.send_message(chat_id, "Amal bekor qilindi.")

    role_chosen(message)  # qayta menyuga qaytaramiz


@bot.message_handler(func=lambda m: m.text in ["Bosh menyu ⏪", "Главное меню ⏪"])
def to_main_menu(message):
    chat_id = message.chat.id
    role_chosen(message)


# ============================================
# CALLBACK — SHAXSIY TELEGRAMINGGA YO‘NALTIRISH
# ============================================
@bot.message_handler(commands=['callback'])
def send_test(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="E'tiroz yuborish ✍🏼",
        url="https://t.me/khakimovvd"   # ❗ BU YERGA O‘Z TELEGRAM LINKINGNI YOZ
    )
    keyboard.add(btn)

    bot.send_message(
        message.chat.id,
        "Agar bot haqida e’tirozlaringiz bo‘lsa pastdagi tugmani bosing 👇🏼",
        reply_markup=keyboard
    )


# ============================================
# BOTNI ISHGA TUSHIRISH
# ============================================
bot.infinity_polling()
