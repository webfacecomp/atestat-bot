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
teacher_stage = {}
teacher_class = {}
teacher_group = {}

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
        bot.send_message(chat_id, "Men sizga qanday yordam bera olaman?")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            "Dars jadvali 📑",
            "ChSB demo 📝",
            "IQ savollar 🧠",
            "Fan testlari 🔖",
            "SAT misollari 📘",
            "Men o‘quvchi emasman"
        )

    bot.send_message(chat_id, "Masalan 👇🏼 :", reply_markup=markup)

# ============================================================
# O‘QITUVCHILAR: YILLIK DARS REJASI BO‘LIMI
# ============================================================


# O‘QITUVCHI MENYUSIGA YANGI COMMAND QO‘SHISH
@bot.message_handler(func=lambda m: m.text in ["Учитель 👨🏻‍🏫", "O‘qituvchi 👨🏻‍🏫"])
def teacher_menu(message):
    chat_id = message.chat.id
    user_role[chat_id] = "teacher"
    lang = user_lang.get(chat_id, "uz")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if lang == "ru":
        markup.add("Годовой план занятий 📘")
        markup.add("Отмена ↩️", "Главное меню ⏪")
        bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)
    else:
        markup.add("Sinflar uchun yillik dars rejasi 📘")
        markup.add("Bekor qilish ↩️", "Bosh menyu ⏪")
        bot.send_message(chat_id, "Kerakli bo‘limni tanlang:", reply_markup=markup)


# ============================================================
# YILLIK REJA — SINF TANLASH
# ============================================================
@bot.message_handler(func=lambda m: m.text in ["Sinflar uchun yillik dars rejasi 📘", "Годовой план занятий 📘"])
def teacher_choose_class(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    teacher_stage[chat_id] = "choose_class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    classes = ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]
    for c in classes:
        markup.add(c)

    text = "Выберите класс:" if lang == "ru" else "Siz qaysi sinf rejasini ko‘rmoqchisiz?"
    bot.send_message(chat_id, text, reply_markup=markup)


# ============================================================
# SINF TANLANGANDA — GURUH TANLASH
# ============================================================
@bot.message_handler(func=lambda m: teacher_stage.get(m.chat.id) == "choose_class" 
                                 and m.text.replace("-sinf", "").isdigit())
def teacher_choose_group(message):
    chat_id = message.chat.id
    sinf = message.text.replace("-sinf", "")

    teacher_class[chat_id] = sinf
    teacher_stage[chat_id] = "choose_group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[sinf]:
        markup.add(g)

    lang = user_lang.get(chat_id, "uz")
    text = "Выберите параллель:" if lang == "ru" else "Qaysi guruh?"
    bot.send_message(chat_id, text, reply_markup=markup)


# ============================================================
# GURUH TANLANGANDA — FANLARNI CHIQARISH
# ============================================================
@bot.message_handler(func=lambda m: teacher_stage.get(m.chat.id) == "choose_group" 
                                 and m.text in sum(groups.values(), []))
def teacher_choose_subject(message):
    chat_id = message.chat.id
    group = message.text
    sinf = int(teacher_class[chat_id])
    teacher_group[chat_id] = group
    teacher_stage[chat_id] = "choose_subject"

    # Fanlar ro‘yxati
    subjects = ["Inglis tili", "Rus tili", "Ona tili", "Adabiyot",
                "Geografiya", "Biologiya"]

    # Maxsus sinflar uchun fanlarni moslashtirish
    if sinf < 7:
        subjects.insert(0, "Matematika")
        subjects.insert(4, "Tarix")
    else:
        subjects.insert(0, "Algebra")
        subjects.insert(1, "Geometriya")
        subjects.insert(4, "O‘zbekiston tarixi")
        subjects.insert(5, "Jahon tarixi")
        subjects.append("Fizika")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for s in subjects:
        markup.add(s)

    # Fan yo‘qligi uchun xabar
    markup.add("Menga kerakli fan yo‘q ❗")

    lang = user_lang.get(chat_id, "uz")
    text = "Выберите предмет:" if lang == "ru" else "Qaysi fan kerak?"
    bot.send_message(chat_id, text, reply_markup=markup)


# ============================================================
# FAN YO‘Q BO‘LSA — JAVOB
# ============================================================
@bot.message_handler(func=lambda m: m.text == "Menga kerakli fan yo‘q ❗")
def subject_missing(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Sizga kerakli fan bu ro‘yxatda bo‘lmasa u tez kunlarda qo‘shiladi ⏳!")


# ============================================================
# FAN TANLANGANDA — HAZIRCHA PLACEHOLDER
# ============================================================
@bot.message_handler(func=lambda m: teacher_stage.get(m.chat.id) == "choose_subject")
def teacher_subject_result(message):
    chat_id = message.chat.id

    if message.text == "Menga kerakli fan yo‘q ❗":
        return  # yuqorida allaqachon ishlov bor

    subject = message.text
    group = teacher_group.get(chat_id)
    sinf = teacher_class.get(chat_id)

    bot.send_message(
        chat_id,
        f"{sinf}-{group} uchun `{subject}` fani bo‘yicha yillik reja tez orada qo‘shiladi ⏳!"
    )


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
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang=="ru":
        markup.add("Отмена ↩️","Главное меню ⏪")
    else:
        markup.add("Bekor qilish ↩️","Bosh menyu ⏪")
    return markup

@bot.message_handler(func=lambda m: m.text in ["Bekor qilish ↩️","Отмена ↩️"])
def cancel_action(message):
    chat_id=message.chat.id
    lang=user_lang.get(chat_id,"uz")
    if lang=="ru":
        bot.send_message(chat_id,"Действие отменено.")
    else:
        bot.send_message(chat_id,"Amal bekor qilindi.")
    role_chosen(message)

@bot.message_handler(func=lambda m: m.text in ["Bosh menyu ⏪","Главное меню ⏪"])
def to_main_menu(message):
    role_chosen(message)


# ============================================
# CALLBACK — SHAXSIY TELEGRAMINGGA YO‘NALTIRISH
# ============================================
@bot.message_handler(commands=['callback'])
def send_test(message):
    keyboard=types.InlineKeyboardMarkup()
    btn=types.InlineKeyboardButton(
        text="E'tiroz yuborish ✍🏼",
        url="https://t.me/khakimovvd" # O‘Z TELEGRAM LINK
    )
    keyboard.add(btn)
    bot.send_message(message.chat.id,"Agar bot haqida e’tirozlaringiz bo‘lsa pastdagi tugmani bosing 👇🏼",reply_markup=keyboard)


# =============================
# BOSHQALAR — TEZ KUNLARDA YO‘Q FUNKSIYA
# =============================
@bot.message_handler(func=lambda m: m.text not in [
    "Dars jadvali 📑","Расписание уроков 📑",
    "5-sinf","6-sinf","7-sinf","8-sinf","9-sinf","10-sinf","11-sinf"
]+sum(groups.values(),[])+
["Men o‘quvchi emasman","Я не ученик","Bekor qilish ↩️","Bosh menyu ⏪","Отмена ↩️","Главное меню ⏪"])
def placeholder(message):
    chat_id=message.chat.id
    lang=user_lang.get(chat_id,"uz")
    if lang=="ru":
        bot.send_message(chat_id,"Скоро эта функция появится! ⏳")
    else:
        bot.send_message(chat_id,"Tez kunlarda bu funksiya qo‘shiladi ⏳")



# ============================================
# BOTNI ISHGA TUSHIRISH
# ============================================
bot.infinity_polling()
