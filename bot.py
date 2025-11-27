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

missing_subject_uz = "Menga kerakli fan yo‘q"
missing_subject_ru = "Нужного предмета нет"

# ============================================================
# CHIROYLİ TUGMALAR (EMOJI + TARTIB)
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
    if lang == "ru":
        markup.add("Годовой план занятий")
    else:
        markup.add("Sinflar uchun yillik dars rejasi")
    return markup

def get_student_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == "ru":
        markup.add("Расписание уроков", "ЧСБ демо")
        markup.add("IQ вопросы", "Тесты по предметам")
        markup.add("SAT задачи", "Я не ученик")
    else:
        markup.add("Dars jadvali", "ChSB demo")
        markup.add("IQ savollar", "Fan testlari")
        markup.add("SAT misollari", "Men o‘quvchi emasman")
    return markup

def get_feedback_inline():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text="E'tiroz yuborish", url="https://t.me/khakimovvd")
    keyboard.add(btn)
    return keyboard

# ============================================================
# /start — TIL TANLASH
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    text = "Assalomu alaykum! Men sizni korganimdan hursandman.\nSiz qaysi tilda suhbatlashmoqchisiz?"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("Rus", "Uzb")
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# TIL TANLANDI → ROL TANLASH
# ============================================================
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

# ============================================================
# ROL TANLANDI → MENYU
# ============================================================
@bot.message_handler(func=lambda m: m.text in [
    "Информация о школе", "Maktab haqida ma'lumot",
    "Учитель", "O‘qituvchi", "Ученик", "O‘quvchi"
])
def role_chosen(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if message.text in ["Информация о школе", "Maktab haqida ma'lumot"]:
        from_chat_id = "@ChortoqTIM"
        message_id = 1  # Kanal post ID (o'zgartiring!)
        try:
            bot.forward_message(chat_id, from_chat_id, message_id)
        except:
            bot.send_message(chat_id, "Ma'lumot yuklanmadi. Kanalga o‘ting: @ChortoqTIM")
        # Qayta rol
        ask = "Вы учитель или ученик?" if lang == "ru" else "Siz o‘qituvchimisiz yoki o‘quvchi?"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        if lang == "ru":
            markup.add("Информация о школе", "Ученик", "Учитель")
        else:
            markup.add("Maktab haqida ma'lumot", "O‘quvchi", "O‘qituvchi")
        bot.send_message(chat_id, ask, reply_markup=markup)
        return

    if "Учитель" in message.text or "O‘qituvchi" in message.text:
        user_role[chat_id] = "teacher"
        bot.send_message(chat_id, "O‘qituvchi bo‘limi ochildi.", reply_markup=get_teacher_menu(lang))
    else:
        user_role[chat_id] = "student"
        bot.send_message(chat_id, "O‘quvchi bo‘limi ochildi.", reply_markup=get_student_menu(lang))

# ============================================================
# O‘QUVCHI: DARS JADVALI
# ============================================================
@bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "student" and m.text in [
    "Dars jadvali", "Расписание уроков"
])
def ask_class(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    user_stage[chat_id] = "choose_class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for c in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        if lang == "ru":
            markup.add(c.replace("-sinf", "-класс"))
        else:
            markup.add(c)
    bot.send_message(chat_id, "Sinifni tanlang:" if lang == "uz" else "Выберите класс:", reply_markup=markup)

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "choose_class")
def choose_group_student(message):
    sinf = message.text.replace("-sinf", "").replace("-класс", "")
    if sinf not in groups:
        return
    user_class[message.chat.id] = sinf
    user_stage[message.chat.id] = "choose_group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for g in groups[sinf]:
        markup.add(g)
    bot.send_message(message.chat.id, "Guruhni tanlang:" if user_lang.get(message.chat.id) == "uz" else "Выберите группу:", reply_markup=markup)

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "choose_group" and m.text in sum(groups.values(), []))
def send_schedule(message):
    group = message.text
    path = f"images/{group}.jpg"
    try:
        with open(path, "rb") as img:
            bot.send_photo(message.chat.id, img, caption=f"{group} dars jadvali")
    except:
        bot.send_message(message.chat.id, "Jadval topilmadi.")
    user_stage.pop(message.chat.id, None)
    user_class.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "Boshqa savollar?", reply_markup=get_student_menu(user_lang.get(message.chat.id, "uz")))

# O‘quvchi boshqa funksiyalari
@bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "student" and m.text not in [
    "Dars jadvali", "Расписание уроков", "Men o‘quvchi emasman", "Я не ученик"
])
def student_other(message):
    bot.send_message(message.chat.id, "Bu funksiya tez orada qo‘shiladi")

# ============================================================
# O‘QITUVCHI: YILLIK REJA
# ============================================================
@bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "teacher" and m.text in [
    "Sinflar uchun yillik dars rejasi", "Годовой план занятий"
])
def teacher_start_plan(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    teacher_mode[chat_id] = True
    teacher_step[chat_id] = "class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for c in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        if lang == "ru":
            markup.add(c.replace("-sinf", "-класс"))
        else:
            markup.add(c)
    for row in teacher_cancel_buttons(lang).keyboard:
        markup.keyboard.append(row)
    bot.send_message(chat_id, "Sinifni tanlang:" if lang == "uz" else "Выберите класс:", reply_markup=markup)

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) and teacher_step.get(m.chat.id) == "class")
def teacher_choose_group(message):
    sinf = message.text.replace("-sinf", "").replace("-класс", "")
    if sinf not in groups:
        return
    teacher_class[message.chat.id] = sinf
    teacher_step[message.chat.id] = "group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for g in groups[sinf]:
        markup.add(g)
    for row in teacher_cancel_buttons(user_lang.get(message.chat.id, "uz")).keyboard:
        markup.keyboard.append(row)
    bot.send_message(message.chat.id, "Guruhni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) and teacher_step.get(m.chat.id) == "group")
def teacher_choose_subject(message):
    if message.text not in sum(groups.values(), []):
        return
    teacher_group[message.chat.id] = message.text
    teacher_step[message.chat.id] = "subject"

    sinf = int(teacher_class.get(message.chat.id))
    lang = user_lang.get(message.chat.id, "uz")
    subjects = subjects_ru[">=7"] if (lang == "ru" and sinf >= 7) else \
               subjects_uz[">=7"] if (lang == "uz" and sinf >= 7) else \
               subjects_ru["<7"] if lang == "ru" else subjects_uz["<7"]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for s in subjects:
        markup.add(s)
    markup.add(missing_subject_ru if lang == "ru" else missing_subject_uz)
    for row in teacher_cancel_buttons(lang).keyboard:
        markup.keyboard.append(row)
    bot.send_message(message.chat.id, "Fan tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) and m.text in [missing_subject_uz, missing_subject_ru])
def teacher_missing_subject(message):
    bot.send_message(message.chat.id, "Tez orada qo‘shiladi")
    teacher_cancel(message)

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id) and teacher_step.get(m.chat.id) == "subject")
def teacher_subject_result(message):
    if message.text in [missing_subject_uz, missing_subject_ru, "Bekor qilish", "Отмена", "Bosh menyu", "Главное меню"]:
        return
    sinf = teacher_class.get(message.chat.id)
    group = teacher_group.get(message.chat.id)
    bot.send_message(message.chat.id, f"{sinf}-{group} → *{message.text}* rejasi tez orada", parse_mode="Markdown")
    teacher_cancel(message)

# ============================================================
# CALLBACK – SILAYDIGAN TUGMA
# ============================================================
@bot.message_handler(commands=['callback'])
def send_test(message):
    bot.send_message(message.chat.id, "E'tiroz bo‘lsa:", reply_markup=get_feedback_inline())

# ============================================================
# RESTART – HAR KIM ISHLATADI
# ============================================================
@bot.message_handler(commands=['restart'])
def universal_restart(message):
    bot.reply_to(message, "Bot qayta ishga tushirilmoqda...")
    print(f"[RESTART] {message.from_user.first_name} ({message.from_user.id})")
    threading.Thread(target=lambda: os._exit(0)).start()

# ============================================================
# BOT ISHGA TUSHADI
# ============================================================
if __name__ == "__main__":
    print("Bot ishga tushdi...")
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print("Xato:", e)
        import time
        time.sleep(5)
        os.execv(__file__, ['python'] + [__file__])

bot.infinity_polling()