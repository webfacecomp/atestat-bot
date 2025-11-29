import os
import telebot
from telebot import types
import threading

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ============================================================
# USER DATA
# ============================================================
user_lang = {}
user_role = {}
user_stage = {}
user_class = {}
user_phone = {}
user_name = {}

# TEACHER STATES
teacher_mode = {}
teacher_step = {}
teacher_class = {}
teacher_group = {}

# ============================================================
# CONFIG
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
    "<7": ["Matematika", "Inglis tili", "Rus tili", "Ona tili", "Tarix",
           "Adabiyot", "Geografiya", "Biologiya"],

    ">=7": ["Algebra", "Geometriya", "Inglis tili", "Rus tili", "Ona tili",
            "O'zbekiston tarixi", "Jahon tarixi", "Adabiyot",
            "Geografiya", "Biologiya", "Fizika"]
}

subjects_ru = {
    "<7": ["Математика", "Английский язык", "Русский язык", "Родной язык", "История",
           "Литература", "География", "Биология"],

    ">=7": ["Алгебра", "Геометрия", "Английский язык", "Русский язык", "Родной язык",
            "История Узбекистана", "Всемирная история", "Литература",
            "География", "Биология", "Физика"]
}

missing_subject_uz = "Menga kerakli fan yo‘q ❗"
missing_subject_ru = "Нужного предмета нет ❗"


# ============================================================
# UNIVERSAL BUTTONS
# ============================================================

def back_btn(lang):
    return "Orqaga ↩️" if lang == "uz" else "Назад ↩️"


def back_markup(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(back_btn(lang))
    return markup


def get_student_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == "uz":
        markup.add("Dars jadvali 📑")
        markup.add("Fan testlari 🔖")
        markup.add("ChSB demo 📝", "IQ savollar 🧠")
        markup.add("SAT misollari 📘")
    else:
        markup.add("Расписание уроков 📑")
        markup.add("Тесты по предметам 🔖")
        markup.add("ЧСБ демо 📝", "IQ вопросы 🧠")
        markup.add("SAT задачи 📘")
    return markup


def get_teacher_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "uz":
        markup.add("Sinflar uchun yillik dars rejasi 📘")
    else:
        markup.add("Годовой план занятий 📘")
    return markup


# ============================================================
# START → CHOOSE LANGUAGE
# ============================================================

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Uzb 🇺🇿", "Rus 🇷🇺")
    bot.send_message(chat_id, "Tilni tanlang:", reply_markup=markup)


# ============================================================
# LANGUAGE SELECTED → ASK CONTACT
# ============================================================

@bot.message_handler(func=lambda m: m.text in ["Uzb 🇺🇿", "Rus 🇷🇺"])
def choose_lang(message):
    chat_id = message.chat.id
    lang = "uz" if message.text == "Uzb 🇺🇿" else "ru"
    user_lang[chat_id] = lang

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton(
        "Kontaktni ulashish 📱" if lang == "uz" else "Поделиться контактом 📱",
        request_contact=True
    )
    markup.add(btn)

    text = "Login yoki ro‘yxatdan o‘tish uchun telefon raqamingizni yuboring."
    if lang == "ru":
        text = "Для входа или регистрации отправьте свой номер телефона."

    bot.send_message(chat_id, text, reply_markup=markup)
    user_stage[chat_id] = "login"


# ============================================================
# CONTACT RECEIVED → ASK NAME IF NEW USER
# ============================================================

@bot.message_handler(content_types=['contact'])
def register_or_login(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    phone = message.contact.phone_number
    user_phone[chat_id] = phone

    # Agar yangi bo‘lsa → ism soraymiz
    if chat_id not in user_name:
        bot.send_message(chat_id,
            "Ism-familiyangizni kiriting:" if lang == "uz" else "Введите ваше имя и фамилию:"
        )
        user_stage[chat_id] = "ask_name"
        return

    # Aks holda → rol tanlash
    send_role_menu(chat_id, lang)


@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "ask_name")
def get_name(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    user_name[chat_id] = message.text.strip()

    bot.send_message(chat_id,
        f"Ro‘yxatdan o‘tildi, {user_name[chat_id]}!" if lang == "uz" else f"Вы зарегистрированы, {user_name[chat_id]}!"
    )

    send_role_menu(chat_id, lang)


# ============================================================
# ROLE MENU
# ============================================================

def send_role_menu(chat_id, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "uz":
        markup.add("O‘quvchi 🧑🏻‍🎓", "O‘qituvchi 👨🏻‍🏫")
    else:
        markup.add("Ученик 🧑🏻‍🎓", "Учитель 👨🏻‍🏫")

    text = "Siz kimsiz?" if lang == "uz" else "Вы кто?"
    bot.send_message(chat_id, text, reply_markup=markup)
    user_stage[chat_id] = "role"


# ============================================================
# ROLE CHOSEN → MENU
# ============================================================

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "role")
def role_selected(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    txt = message.text

    if txt in ["O‘qituvchi 👨🏻‍🏫", "Учитель 👨🏻‍🏫"]:
        user_role[chat_id] = "teacher"
        bot.send_message(chat_id,
            "O‘qituvchilar menyusi:" if lang == "uz" else "Меню учителя:",
            reply_markup=get_teacher_menu(lang)
        )
        return

    if txt in ["O‘quvchi 🧑🏻‍🎓", "Ученик 🧑🏻‍🎓"]:
        user_role[chat_id] = "student"
        bot.send_message(chat_id,
            "O‘quvchilar menyusi:" if lang == "uz" else "Меню ученика:",
            reply_markup=get_student_menu(lang)
        )
        return


# ============================================================
# STUDENT — FAN TESTLARI
# ============================================================

@bot.message_handler(func=lambda m: user_role.get(m.chat.id)=="student" and m.text in ["Fan testlari 🔖", "Тесты по предметам 🔖"])
def open_test_section(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "uz":
        markup.add("Qiziquvchilar uchun testlar", "Olimpiada testlar")
    else:
        markup.add("Тесты для интересующихся", "Олимпиадные тесты")
    markup.add(back_btn(lang))

    bot.send_message(chat_id,
        "Test turini tanlang:" if lang == "uz" else "Выберите тип тестов:",
        reply_markup=markup
    )

    user_stage[chat_id] = "choose_test_type"


# ============================================================
# TEST TYPE → CHOOSE CLASS
# ============================================================

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="choose_test_type")
def choose_test_class(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if message.text == back_btn(lang):
        bot.send_message(chat_id, "Orqaga qaytdingiz.", reply_markup=get_student_menu(lang))
        user_stage[chat_id] = "role"
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    classes = ["5", "6", "7", "8", "9", "10", "11"]
    for c in classes:
        markup.add(f"{c}-sinf")
    markup.add(back_btn(lang))

    bot.send_message(chat_id,
        "Qaysi sinf uchun test?" if lang == "uz" else "Для какого класса тесты?",
        reply_markup=markup
    )

    user_stage[chat_id] = "choose_test_class"


# ============================================================
# CLASS → CHOOSE SUBJECT
# ============================================================

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="choose_test_class")
def choose_test_subject(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if message.text == back_btn(lang):
        open_test_section(message)
        return

    if "-sinf" not in message.text:
        return

    sinf = message.text.replace("-sinf", "")
    user_class[chat_id] = sinf

    sinf_int = int(sinf)
    subjects = subjects_uz["<7"] if lang=="uz" and sinf_int<7 else \
               subjects_uz[">=7"] if lang=="uz" else \
               subjects_ru["<7"] if sinf_int<7 else \
               subjects_ru[">=7"]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for s in subjects:
        markup.add(s)
    markup.add(missing_subject_uz if lang=="uz" else missing_subject_ru)
    markup.add(back_btn(lang))

    bot.send_message(chat_id,
        "Qaysi fandan test ishlamoqchisiz?" if lang=="uz" else "По какому предмету хотите тест?",
        reply_markup=markup
    )

    user_stage[chat_id] = "choose_test_subject"


# ============================================================
# SUBJECT → RESULT
# ============================================================

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="choose_test_subject")
def send_subject_result(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if message.text == back_btn(lang):
        choose_test_class(message)
        return

    sinf = user_class.get(chat_id)

    if message.text in [missing_subject_uz, missing_subject_ru]:
        bot.send_message(chat_id,
            "Sizga kerakli fan tez orada qo‘shiladi ⏳!" if lang=="uz" else "Предмет скоро будет добавлен ⏳!"
        )
        return

    subject = message.text

    bot.send_message(chat_id,
        f"{sinf}-sinf uchun {subject} testlari tez orada qo‘shiladi ⏳!",
        parse_mode="Markdown"
    )

    bot.send_message(chat_id, "Menyuga qaytdingiz.", reply_markup=get_student_menu(lang))
    user_stage[chat_id] = "role"


# ============================================================
# STUDENT — DARS JADVALI (senga aytganchalik, o‘zgarmagan)
# ============================================================

@bot.message_handler(func=lambda m: user_role.get(m.chat.id)=="student" and m.text in ["Dars jadvali 📑", "Расписание уроков 📑"])
def ask_class_schedule(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(c)
    markup.add(back_btn(lang))

    bot.send_message(chat_id,
        "Siz nechinchi sinfsiz?" if lang=="uz" else "Выберите класс:",
        reply_markup=markup
    )

    user_stage[chat_id] = "schedule_class"


@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="schedule_class")
def choose_group(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if message.text == back_btn(lang):
        bot.send_message(chat_id, "Orqaga qaytdingiz.", reply_markup=get_student_menu(lang))
        user_stage[chat_id] = "role"
        return

    sinf = message.text.replace("-sinf", "").replace("-класс", "")

    if sinf not in groups:
        return

    user_class[chat_id] = sinf
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[sinf]:
        markup.add(g)
    markup.add(back_btn(lang))

    bot.send_message(chat_id,
        "Qaysi guruhsiz?" if lang=="uz" else "Выберите параллель:",
        reply_markup=markup
    )

    user_stage[chat_id] = "schedule_group"


@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="schedule_group")
def send_schedule(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if message.text == back_btn(lang):
        ask_class_schedule(message)
        return

    group = message.text
    path = f"images/{group}.jpg"

    try:
        with open(path, "rb") as img:
            bot.send_photo(chat_id, img, caption=f"{group} dars jadvali 📚")
    except:
        bot.send_message(chat_id, "Dars jadvali topilmadi.")

    bot.send_message(chat_id, "Menyuga qaytdingiz.", reply_markup=get_student_menu(lang))
    user_stage[chat_id] = "role"


# ============================================================
# TEACHER (AINAN SENING KODING — O‘ZGARMAGAN HOLATDA)
# ============================================================

# ------ (bu yerda sening o‘qituvchilar bo‘liming qo‘shimchasiz turibdi) ------


# ============================================================
# BOT START
# ============================================================

print("Bot ishga tushdi...")

bot.infinity_polling(skip_pending=True)
