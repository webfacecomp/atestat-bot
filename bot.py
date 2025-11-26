import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

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
# /start — LANGUAGE CHOOSE
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Rus 🇷🇺", "Uzb 🇺🇿")

    bot.send_message(
        message.chat.id,
        "Assalomu alaykum!\nSiz qaysi tilda suhbatlashishni xohlaysiz?",
        reply_markup=markup
    )

# ============================================================
# LANGUAGE SELECTED → ROLE SELECT
# ============================================================
@bot.message_handler(func=lambda m: m.text in ["Rus 🇷🇺", "Uzb 🇺🇿"])
def choose_lang(message):
    chat_id = message.chat.id

    if message.text == "Rus 🇷🇺":
        lang = "ru"
        msg = "Вы выбрали русский язык."
        ask = "Вы учитель или ученик?"
        teacher = "Учитель 👨🏻‍🏫"
        student = "Ученик 🧑🏻‍🎓"
    else:
        lang = "uz"
        msg = "Siz o‘zbek tilini tanladingiz."
        ask = "Siz o‘qituvchimisiz yoki o‘quvchi?"
        teacher = "O‘qituvchi 👨🏻‍🏫"
        student = "O‘quvchi 🧑🏻‍🎓"

    user_lang[chat_id] = lang
    bot.send_message(chat_id, msg)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(teacher, student)

    bot.send_message(chat_id, ask, reply_markup=markup)

# ============================================================
# ROLE CHOSEN → MENU
# ============================================================
@bot.message_handler(func=lambda m: m.text in [
    "Учитель 👨🏻‍🏫", "Ученик 🧑🏻‍🎓",
    "O‘qituvchi 👨🏻‍🏫", "O‘quvchi 🧑🏻‍🎓"
])
def role_chosen(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    # TEACHER
    if message.text in ["Учитель 👨🏻‍🏫", "O‘qituvchi 👨🏻‍🏫"]:
        user_role[chat_id] = "teacher"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            "Sinflar uchun yillik dars rejasi 📘" if lang == "uz"
            else "Годовой план занятий 📘"
        )

        markup.add(
            "Bosh menyu ⏪" if lang == "uz" else "Главное меню ⏪"
        )

        bot.send_message(
            chat_id,
            "Hozircha o‘qituvchilar uchun ayrim funksiyalar mavjud." if lang == "uz"
            else "Сейчас доступны только некоторые функции для учителей.",
            reply_markup=markup
        )
        return

    # STUDENT
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

# ============================================================
# “Not student” → ask role again
# ============================================================
@bot.message_handler(func=lambda m: m.text in ["Men o‘quvchi emasman", "Я не ученик"])
def not_student(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "ru":
        markup.add("Учитель 👨🏻‍🏫", "Ученик 🧑🏻‍🎓")
        bot.send_message(chat_id, "Выберите роль снова.", reply_markup=markup)
    else:
        markup.add("O‘qituvchi 👨🏻‍🏫", "O‘quvchi 🧑🏻‍🎓")
        bot.send_message(chat_id, "Rolni qaytadan tanlang.", reply_markup=markup)

# ============================================================
# DARS JADVALI — ASK CLASS
# ============================================================
@bot.message_handler(func=lambda m: m.text in ["Dars jadvali 📑", "Расписание уроков 📑"])
def ask_class(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    user_stage[chat_id] = "choose_class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(c)

    bot.send_message(
        chat_id,
        "Выберите класс:" if lang == "ru" else "Siz nechinchi sinfsiz?",
        reply_markup=markup
    )

# ============================================================
# GROUPS
# ============================================================
groups = {
    "5": ["5-01", "5-02"],
    "6": ["6-01", "6-02"],
    "7": ["7-01", "7-02", "7-03"],
    "8": ["8-01", "8-02", "8-03"],
    "9": ["9-01", "9-02", "9-03"],
    "10": ["10-01", "10-02", "10-03"],
    "11": ["11-01", "11-02", "11-03"],
}

# ============================================================
# CHOOSE GROUP
# ============================================================
@bot.message_handler(func=lambda m: m.text.endswith("-sinf"))
def choose_group(message):
    chat_id = message.chat.id
    sinf = message.text.replace("-sinf", "")
    user_class[chat_id] = sinf
    user_stage[chat_id] = "choose_group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[sinf]:
        markup.add(g)

    lang = user_lang.get(chat_id, "uz")

    bot.send_message(
        chat_id,
        "Выберите группу:" if lang == "ru" else "Siz qaysi guruhsiz?",
        reply_markup=markup
    )

# ============================================================
# SEND SCHEDULE IMAGE
# ============================================================
@bot.message_handler(func=lambda m: m.text in sum(groups.values(), []))
def send_schedule(message):
    chat_id = message.chat.id
    group = message.text

    path = os.path.join(os.path.dirname(__file__), "images", f"{group}.jpg")

    try:
        with open(path, "rb") as img:
            bot.send_photo(chat_id, img, caption=f"{group} dars jadvali 📚")
    except:
        bot.send_message(chat_id, "Dars jadvali mavjud emas.")

# ============================================================
#   O‘QITUVCHI BO‘LIMI — YILLIK DARS REJASI
# ============================================================

# Teacher uchun vaqtinchalik saqlovchi maydonlar
teacher_mode = {}
teacher_step = {}
teacher_class = {}
teacher_group = {}

# BOSHQARILADIGAN FUNKSIYA
def teacher_cancel_buttons(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "ru":
        markup.add("Отмена ↩️", "Главное меню ⏪")
    else:
        markup.add("Bekor qilish ↩️", "Bosh menyu ⏪")
    return markup


# ============================================================
#   1-QADAM – YILLIK REJA MENYUSI
# ============================================================

@bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "teacher" and m.text in [
    "Sinflar uchun yillik dars rejasi 📘",
    "Годовой план занятий 📘"
])
def teacher_start_plan(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    teacher_mode[chat_id] = True
    teacher_step[chat_id] = "class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(c)

    # Cancel & Main Menu
    for b in teacher_cancel_buttons(lang).keyboard:
        markup.keyboard.append(b)

    bot.send_message(
        chat_id,
        "Выберите класс:" if lang == "ru" else "Siz qaysi sinfni tanlaysiz?",
        reply_markup=markup
    )


# ============================================================
#   2-QADAM – PARALLEL (5-01, 7-03 …)
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) and teacher_step.get(m.chat.id) == "class")
def teacher_choose_group(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = message.text

    if not text.endswith("-sinf"):
        return

    sinf = text.replace("-sinf", "")
    teacher_class[chat_id] = sinf
    teacher_step[chat_id] = "group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[sinf]:
        markup.add(g)

    # Cancel & Main Menu
    for b in teacher_cancel_buttons(lang).keyboard:
        markup.keyboard.append(b)

    bot.send_message(
        chat_id,
        "Выберите параллель:" if lang == "ru" else "Qaysi guruh?",
        reply_markup=markup
    )


# ============================================================
#   3-QADAM – FANLARNI TANLASH (dinamik)
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) and teacher_step.get(m.chat.id) == "group")
def teacher_choose_subject(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = message.text

    if text not in sum(groups.values(), []):
        return

    group = text
    sinf = int(teacher_class.get(chat_id))

    teacher_group[chat_id] = group
    teacher_step[chat_id] = "subject"

    # FANNI DINAMIK TANLASH 
    subjects = ["Inglis tili", "Rus tili", "Ona tili", "Adabiyot", "Geografiya", "Biologiya"]

    if sinf < 7:
        subjects.insert(0, "Matematika")
        subjects.insert(3, "Tarix")
    else:
        subjects = [
            "Algebra", "Geometriya",
            "Inglis tili", "Rus tili", "Ona tili",
            "O'zbekiston tarixi", "Jahon tarixi",
            "Adabiyot", "Geografiya", "Biologiya", "Fizika"
        ]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for s in subjects:
        markup.add(s)

    markup.add("Menga kerakli fan yo‘q ❗")

    # Cancel & Main Menu
    for b in teacher_cancel_buttons(lang).keyboard:
        markup.keyboard.append(b)

    bot.send_message(
        chat_id,
        "Выберите предмет:" if lang == "ru" else "Qaysi fan kerak?",
        reply_markup=markup
    )


# ============================================================
#   “Fan yo‘q” – maxsus xabar
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) and m.text == "Menga kerakli fan yo‘q ❗")
def teacher_missing_subject(message):
    bot.send_message(message.chat.id, "Bu fan tez orada qo‘shiladi ⏳!")


# ============================================================
#   4-QADAM – FAN TANLANGANDA YAKUNIY HABAR
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) and teacher_step.get(m.chat.id) == "subject")
def teacher_subject_result(message):
    chat_id = message.chat.id
    subject = message.text
    sinf = teacher_class.get(chat_id)
    group = teacher_group.get(chat_id)

    bot.send_message(
        chat_id,
        f"{sinf}-{group} sinf uchun *{subject}* fanidan yillik dars rejasi tez orada qo‘shiladi ⏳!",
        parse_mode="Markdown"
    )

    # Reset
    teacher_mode[chat_id] = False
    teacher_step[chat_id] = None


# ============================================================
# CALLBACK → SHAXSIY TELEGRAM LINK
# ============================================================
@bot.message_handler(commands=['callback'])
def send_test(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="E'tiroz yuborish ✍🏼",
        url="https://t.me/khakimovvd"
    )
    keyboard.add(btn)

    bot.send_message(
        message.chat.id,
        "Agar bot haqida e’tirozlaringiz bo‘lsa pastdagi tugmani bosing 👇🏼",
        reply_markup=keyboard
    )

# ============================================================
# BOT START
# ============================================================
bot.infinity_polling()
