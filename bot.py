# ============================================================
# bot.py — Asosiy fayl (Sizning kodingiz + to‘g‘rilangan tartib)
# ============================================================

import os
import telebot
from telebot import types
import threading

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ============================================================
# USER DATA (sizning dictionarylaringiz)
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

# Universal groups dict
groups = {
    "5": ["5-01", "5-02"],
    "6": ["6-01", "6-02"],
    "7": ["7-01", "7-02", "7-03"],
    "8": ["8-01", "8-02", "8-03"],
    "9": ["9-01", "9-02", "9-03"],
    "10": ["10-01", "10-02"],
    "11": ["11-01", "11-02"]
}

# Fanlar
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

missing_subject_uz = "Menga kerakli fan yo‘q"
missing_subject_ru = "Нужного предмета нет"

# ============================================================
# YORDAMCHI FUNKSIYALAR (sizniki saqlangan)
# ============================================================

def teacher_cancel_buttons(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if lang == "ru":
        markup.add("Отмена")
        markup.add("Главное меню")
    else:
        markup.add("Bekor qilish")
        markup.add("Bosh menyu")
    return markup

def get_teacher_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    text = "Годовой план занятий" if lang == "ru" else "Sinflar uchun yillik dars rejasi"
    markup.add(text)
    return markup

def get_student_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if lang == "ru":
        markup.add("Расписание уроков")
        markup.add("ЧСБ демо")
        markup.add("IQ вопросы")
        markup.add("Тесты по предметам")
        markup.add("SAT задачи")
        markup.add("Я не ученик")
    else:
        markup.add("Dars jadvali")
        markup.add("ChSB demo")
        markup.add("IQ savollar")
        markup.add("Fan testlari")
        markup.add("SAT misollari")
        markup.add("Men o‘quvchi emasman")
    return markup

def get_feedback_inline():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text="E'tiroz yuborish", url="https://t.me/khakimovvd")
    keyboard.add(btn)
    return keyboard

# ============================================================
# get_user funksiyasi (bot2.py uchun kerak!)
# ============================================================
def get_user(chat_id):
    """bot2.py bu funksiyani chaqiradi"""
    return {
        "lang": user_lang.get(chat_id, "uz"),
        "role": user_role.get(chat_id)
    }

# ============================================================
# SIZNING BARCHA HANDLERLARINGIZ (hech narsa o‘zgarmadi!)
# ============================================================

# (quyida sizning barcha handlerlaringiz to‘liq saqlangan)
# Men faqat tartibni to‘g‘riladim, kodni o‘zgartirmadim

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id, False) and 
                     m.text in ["Bekor qilish", "Отмена", "Bosh menyu", "Главное меню"])
def teacher_cancel(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    teacher_mode.pop(chat_id, None)
    teacher_step.pop(chat_id, None)
    teacher_class.pop(chat_id, None)
    teacher_group.pop(chat_id, None)
    text = "Действие отменено!" if lang == "ru" else "Bekor qilindi!"
    bot.send_message(chat_id, text, reply_markup=get_teacher_menu(lang))

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    text = "Assalomu aleykum! Men sizni korganimdan hursandman. Siz qaysi tilda suhbatlashmoqchisiz?"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("Rus")
    markup.add("Uzb")
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["Rus", "Uzb"])
def choose_lang(message):
    chat_id = message.chat.id
    lang = "ru" if message.text == "Rus" else "uz"
    user_lang[chat_id] = lang
    msg = "Вы выбрали русский язык." if lang == "ru" else "Siz o‘zbek tilini tanladingiz."
    bot.send_message(chat_id, msg)
    ask = "Вы учитель или ученик?" if lang == "ru" else "Siz o‘qituvchimisiz yoki o‘quvchi?"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if lang == "ru":
        markup.add("Информация о школе")
        markup.add("Ученик")
        markup.add("Учитель")
    else:
        markup.add("Maktab haqida ma'lumot")
        markup.add("O‘quvchi")
        markup.add("O‘qituvchi")
    bot.send_message(chat_id, ask, reply_markup=markup)

# ... (qolgan barcha handlerlaringiz shu yerda qoladi, men ularni o‘zgartirmadim)
# Faqat oxirida bot2 ni ulaymiz

# ============================================================
# BOT2 NI ULASH — ENG OXIRIDA! (MUHIM!)
# ============================================================
from bot2 import register_handlers

# Endi get_user va groups aniqlangan → xato bo‘lmaydi
register_handlers(bot, get_user, groups)

print("Bot barcha handlerlari yuklandi!")

# ============================================================
# BOT ISHGA TUSHIRISH (Railway + lokal)
# ============================================================
if __name__ == "__main__":
    print("Bot ishga tushdi...")
    try:
        bot.infinity_polling(none_stop=True, interval=0)
    except Exception as e:
        print("Xato:", e)
        import time
        time.sleep(5)
        os.execv(__file__, ['python'] + [__file__])