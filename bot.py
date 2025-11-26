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

# BOSHQARILADIGAN FUNKSIYA
def teacher_cancel_buttons(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "ru":
        markup.add("Отмена ↩️", "Главное меню ⏪")
    else:
        markup.add("Bekor qilish ↩️", "Bosh menyu ⏪")
    return markup


# ============================================================
#   GURUHLAR VA FANLAR KONFIGURATSIYASI
# ============================================================

# Parallellar (siz tasvirlaganidek)
groups = {
    "5": ["5-01", "5-02"],
    "6": ["6-01", "6-02"],
    "7": ["7-01", "7-02", "7-03"],
    "8": ["8-01", "8-02", "8-03"],
    "9": ["9-01", "9-02", "9-03"],
    "10": ["10-01", "10-02"],
    "11": ["11-01", "11-02"]
}

# Fanlar — tillarga qarab
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

# Kerakli fan yo'q tugmasi
missing_subject_uz = "Menga kerakli fan yo‘q ❗"
missing_subject_ru = "Нужного предмета нет ❗"

# ============================================================
#   BEKOR QILISH VA BOSHMENU TUGMALARI
# ============================================================

def teacher_cancel_buttons(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == "ru":
        markup.add("Отмена ↩️", "Главное меню ⏪")
    else:
        markup.add("Bekor qilish ↩️", "Bosh menyu ⏪")
    return markup


# ============================================================
#   BEKOR QILISH HANDLERI
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) and 
                     m.text in ["Bekor qilish ↩️", "Отмена ↩️", "Bosh menyu ⏪", "Главное меню ⏪"])
def teacher_cancel(message):
    chat_id = message.chat.id
    
    # Holatni tozalash
    teacher_mode[chat_id] = False
    teacher_step[chat_id] = None
    teacher_class.pop(chat_id, None)
    teacher_group.pop(chat_id, None)
    
    lang = user_lang.get(chat_id, "uz")
    text = "Действие отменено!" if lang == "ru" else "Bekor qilindi!"
    
    # Bosh menyuga qaytish (asosiy kodingizdagi main_menu_markup ni chaqiring)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Bu yerda asosiy menyu markupini qo'ying
    bot.send_message(chat_id, text, reply_markup=markup)


# ============================================================
#   1-QADAM – SINFLAR TANLASH
# ============================================================

@bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "teacher" and 
                     m.text in ["Sinflar uchun yillik dars rejasi 📘", "Годовой план занятий 📘"])
def teacher_start_plan(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    # Holatni boshlash
    teacher_mode[chat_id] = True
    teacher_step[chat_id] = "class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    classes = ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]
    for c in classes:
        if lang == "ru":
            ru_class = c.replace("-sinf", "-класс")
            markup.add(ru_class)
        else:
            markup.add(c)

    # Bekor tugmalari
    cancel_markup = teacher_cancel_buttons(lang)
    for row in cancel_markup.keyboard:
        markup.keyboard.append(row)

    text = "Выберите класс:" if lang == "ru" else "Siz qaysi sinfning rejasini bilmoqchisiz?"
    bot.send_message(chat_id, text, reply_markup=markup)


# ============================================================
#   2-QADAM – GURUH TANLASH
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) == True and 
                     teacher_step.get(m.chat.id) == "class")
def teacher_choose_group(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = message.text.strip()

    # Sinfni aniqlash (uz/ru)
    sinf = None
    if "-sinf" in text:
        sinf = text.replace("-sinf", "")
    elif "-класс" in text:
        sinf = text.replace("-класс", "")
    
    if sinf not in groups:
        return  # Noto'g'ri sinf — e'tiborsiz qoldirish

    try:
        sinf_int = int(sinf)
    except ValueError:
        return

    teacher_class[chat_id] = sinf
    teacher_step[chat_id] = "group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for g in groups[sinf]:
        markup.add(g)

    # Bekor tugmalari
    cancel_markup = teacher_cancel_buttons(lang)
    for row in cancel_markup.keyboard:
        markup.keyboard.append(row)

    text = "Выберите параллель:" if lang == "ru" else "Qaysi guruhni tanlaysiz?"
    bot.send_message(chat_id, text, reply_markup=markup)


# ============================================================
#   3-QADAM – FANLAR TANLASH
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) == True and 
                     teacher_step.get(m.chat.id) == "group")
def teacher_choose_subject(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = message.text.strip()

    # Guruhni tekshirish
    all_groups = sum(groups.values(), [])
    if text not in all_groups:
        return

    teacher_group[chat_id] = text
    teacher_step[chat_id] = "subject"

    sinf = teacher_class.get(chat_id)
    sinf_int = int(sinf)

    # Fanlarni tanlash
    if sinf_int < 7:
        subjects = subjects_ru["<7"] if lang == "ru" else subjects_uz["<7"]
    else:
        subjects = subjects_ru[">=7"] if lang == "ru" else subjects_uz[">=7"]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for s in subjects:
        markup.add(s)

    # Kerakli fan yo'q
    missing_btn = missing_subject_ru if lang == "ru" else missing_subject_uz
    markup.add(missing_btn)

    # Bekor tugmalari
    cancel_markup = teacher_cancel_buttons(lang)
    for row in cancel_markup.keyboard:
        markup.keyboard.append(row)

    text = "Выберите предмет:" if lang == "ru" else "Qaysi fan rejasi kerak?"
    bot.send_message(chat_id, text, reply_markup=markup)


# ============================================================
#   KERAKLI FAN YO'Q HANDLERI
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) == True and 
                     m.text in [missing_subject_uz, missing_subject_ru])
def teacher_missing_subject(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    
    text = "Sizga kerakli fan bu ro'yhatda bo'lmasa, u tez kunlarda qo'shiladi ⏳!" if lang == "uz" else "Если нужного предмета нет в списке, он будет добавлен в ближайшее время ⏳!"
    
    bot.send_message(chat_id, text)
    
    # Reset
    teacher_cancel(message)


# ============================================================
#   4-QADAM – FAN TANLANGANIDA NATIJA
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) == True and 
                     teacher_step.get(m.chat.id) == "subject" and
                     m.text not in [missing_subject_uz, missing_subject_ru, "Bekor qilish ↩️", "Отмена ↩️", "Bosh menyu ⏪", "Главное меню ✂️"])
def teacher_subject_result(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    subject = message.text
    
    sinf = teacher_class.get(chat_id)
    group = teacher_group.get(chat_id)
    
    text = f"{sinf}-{group} sinf uchun *{subject}* fanidan yillik dars rejasi tez orada qo‘shiladi ⏳!" if lang == "uz" else f"Годовой план по *{subject}* для {sinf}-{group} класса будет добавлен в ближайшее время ⏳!"
    
    bot.send_message(chat_id, text, parse_mode="Markdown")
    
    # Reset
    teacher_cancel(message)


# ============================================================
# CALLBACK → SHAXSIY TELEGRAM LINK
# ============================================================
@bot.message_handler(commands=['feedback'])
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
