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
