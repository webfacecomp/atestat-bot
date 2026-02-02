import os
import telebot
from telebot import types
import threading

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ============================================================
# MAJBURIY KANAL
# ============================================================
CHANNEL_ID = "@your_channel_username"  # masalan: "@my_school_channel"

# ============================================================
# USER DATA
# ============================================================
user_lang = {}
user_role = {}
user_stage = {}
user_class = {}

# TEACHER STATES
teacher_mode = {}
teacher_step = {}
teacher_class = {}
teacher_group = {}

# ============================================================
# KONFIGURATSIYALAR
# ============================================================
groups = {
    "5": ["5-01", "5-02"],
    "6": ["6-01", "6-02"],
    "7": ["7-01", "7-02", "7-03"],
    "8": ["8-01", "8-02", "8-03"],
    "9": ["9-01", "9-02", "9-03"],
    "10": ["10-01", "10-02"],
    "11": ["11-01", "11-02"]
}

subjects_uz = {
    "<7": ["Matematika", "Inglis tili", "Rus tili", "Ona tili", "Tarix", "Adabiyot", "Geografiya", "Biologiya"],
    ">=7": ["Algebra", "Geometriya", "Inglis tili", "Rus tili", "Ona tili",
            "O'zbekiston tarixi", "Jahon tarixi", "Adabiyot", "Geografiya", "Biologiya", "Fizika"]
}

subjects_ru = {
    "<7": ["Математика", "Английский язык", "Русский язык", "Родной язык", "История", "Литература", "География", "Биология"],
    ">=7": ["Алгебра", "Геометрия", "Английский язык", "Русский язык", "Родной язык",
            "История Узбекистана", "Всемирная история", "Литература", "География", "Биология", "Физика"]
}

missing_subject_uz = "Menga kerakli fan yo‘q ❗"
missing_subject_ru = "Нужного предмета нет ❗"

# ============================================================
# KANALGA OBUNA TEKSHIRUV
# ============================================================
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def ask_subscription(chat_id, lang):
    text = (
        "Davom etish uchun kanalga obuna bo‘lishingizni so‘rayman 📢"
        if lang == "uz"
        else "Для продолжения, пожалуйста, подпишитесь на канал 📢"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "Kanalga o‘tish 🔔" if lang == "uz" else "Перейти в канал 🔔",
            url=f"https://t.me/{CHANNEL_ID.replace('@','')}"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "Tekshirish ✅" if lang == "uz" else "Проверить ✅",
            callback_data="check_sub"
        )
    )

    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# CALLBACK — OBUNA TEKSHIRISH
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    chat_id = call.message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if is_subscribed(chat_id):
        bot.answer_callback_query(call.id, "Rahmat! ✅" if lang == "uz" else "Спасибо! ✅")

        ask = "Вы учитель или ученик?" if lang == "ru" else "Siz o‘qituvchimisiz yoki o‘quvchi?"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

        if lang == "ru":
            markup.add("Информация о школе")
            markup.add("Ученик 🧑🏻‍🎓")
            markup.add("Учитель 👨🏻‍🏫")
        else:
            markup.add("Maktab haqida ma'lumot")
            markup.add("O‘quvchi 🧑🏻‍🎓")
            markup.add("O‘qituvchi 👨🏻‍🏫")

        bot.send_message(chat_id, ask, reply_markup=markup)
    else:
        bot.answer_callback_query(
            call.id,
            "Avval kanalga obuna bo‘ling ❗" if lang == "uz" else "Сначала подпишитесь на канал ❗",
            show_alert=True
        )

# ============================================================
# /start
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Rus 🇷🇺", "Uzb 🇺🇿")
    bot.send_message(chat_id, "Qaysi tilda davom etamiz?", reply_markup=markup)

# ============================================================
# LANGUAGE SELECT
# ============================================================
@bot.message_handler(func=lambda m: m.text in ["Rus 🇷🇺", "Uzb 🇺🇿"])
def choose_lang(message):
    chat_id = message.chat.id
    lang = "ru" if message.text == "Rus 🇷🇺" else "uz"
    user_lang[chat_id] = lang

    if not is_subscribed(chat_id):
        ask_subscription(chat_id, lang)
        return

    ask = "Вы учитель или ученик?" if lang == "ru" else "Siz o‘qituvchimisiz yoki o‘quvchi?"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    if lang == "ru":
        markup.add("Информация о школе")
        markup.add("Ученик 🧑🏻‍🎓")
        markup.add("Учитель 👨🏻‍🏫")
    else:
        markup.add("Maktab haqida ma'lumot")
        markup.add("O‘quvchi 🧑🏻‍🎓")
        markup.add("O‘qituvchi 👨🏻‍🏫")

    bot.send_message(chat_id, ask, reply_markup=markup)

# ============================================================
# BOT START
# ============================================================
if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling(none_stop=True)
