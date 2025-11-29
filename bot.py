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
# KONFIGURATSIYALAR (BITTA JOYDA!)
# ============================================================

# Universal groups dict (ikkalasiga ham ishlatiladi)
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
# YORDAMCHI FUNKSIYALAR
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
# BOT2 UCHUN KERAKLI get_user FUNKSİYASI (qo‘shildi!)
# ============================================================
def get_user(chat_id):
    return {
        "lang": user_lang.get(chat_id, "uz"),
        "role": user_role.get(chat_id)
    }

# ============================================================
# BEKOR QILISH HANDLERI (O'QITUVCHI UCHUN)
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id, False) and 
                     m.text in ["Bekor qilish", "Отмена", "Bosh menyu", "Главное меню"])
def teacher_cancel(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    
    # Holatni tozalash
    teacher_mode.pop(chat_id, None)
    teacher_step.pop(chat_id, None)
    teacher_class.pop(chat_id, None)
    teacher_group.pop(chat_id, None)
    
    text = "Действие отменено!" if lang == "ru" else "Bekor qilindi!"
    bot.send_message(chat_id, text, reply_markup=get_teacher_menu(lang))

# ============================================================
# /start — LANGUAGE CHOOSE
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    text = "Assalomu aleykum! Men sizni korganimdan hursandman. Siz qaysi tilda suhbatlashmoqchisiz?"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("Rus")
    markup.add("Uzb")
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# LANGUAGE SELECTED → ROLE SELECT
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
# ROLE CHOSEN → MENU
# ============================================================
@bot.message_handler(func=lambda m: m.text in ["Информация о школе", "Maktab haqida ma'lumot", "Учитель", "O‘qituvchi", "Ученик", "O‘quvchi"])
def role_chosen(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    if message.text in ["Информация о школе", "Maktab haqida ma'lumot"]:
        from_chat_id = ""  # Kanal username yoki ID
        message_id = 1
        
        try:
            bot.forward_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id)
        except Exception as e:
            bot.send_message(chat_id, f"Xato: {e}. Kanal ma'lumotini yuklab bo'lmadi.")
        
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
        return

    if "Учитель" in message.text or "O‘qituvchi" in message.text:
        user_role[chat_id] = "teacher"
        text = "Hozircha o‘qituvchilar uchun ayrim funksiyalar mavjud." if lang == "uz" else "Сейчас доступны только некоторые функции для учителей."
        bot.send_message(chat_id, text, reply_markup=get_teacher_menu(lang))
    else:
        user_role[chat_id] = "student"
        text = "Menga sizga qanday yordam kerak?" if lang == "uz" else "Как я могу помочь вам?"
        bot.send_message(chat_id, text)
        bot.send_message(chat_id, "Quyidagilardan birini tanlang:" if lang == "uz" else "Выберите один из вариантов:", reply_markup=get_student_menu(lang))

# ============================================================
# “Not student” → ask role again
# ============================================================
@bot.message_handler(func=lambda m: m.text in ["Men o‘quvchi emasman", "Я не ученик"])
def not_student(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if lang == "ru":
        markup.add("Информация о школе")
        markup.add("Ученик")
        markup.add("Учитель")
    else:
        markup.add("Maktab haqida ma'lumot")
        markup.add("O‘quvchi")
        markup.add("O‘qituvchi")
    text = "Выберите роль снова." if lang == "ru" else "Rolni qaytadan tanlang."
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# STUDENT: DARS JADVALI — ASK CLASS
# ============================================================
@bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "student" and m.text in ["Dars jadvali", "Расписание уроков"])
def ask_class(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    user_stage[chat_id] = "choose_class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    classes = ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]
    for c in classes:
        if lang == "ru":
            markup.add(c.replace("-sinf", "-класс"))
        else:
            markup.add(c)

    text = "Выберите класс:" if lang == "ru" else "Siz nechinchi sinfsiz?"
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# STUDENT: CHOOSE GROUP
# ============================================================
@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "choose_class")
def choose_group(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = message.text.strip()

    sinf = None
    if "-sinf" in text:
        sinf = text.replace("-sinf", "")
    elif "-класс" in text:
        sinf = text.replace("-класс", "")

    if not sinf or sinf not in groups:
        return

    user_class[chat_id] = sinf
    user_stage[chat_id] = "choose_group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for g in groups[sinf]:
        markup.add(g)

    text = "Выберите группу:" if lang == "ru" else "Siz qaysi guruhsiz?"
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# STUDENT: SEND SCHEDULE IMAGE
# ============================================================
@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "choose_group" and m.text in sum(groups.values(), []))
def send_schedule(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    group = message.text

    path = f"images/{group}.jpg"

    try:
        with open(path, "rb") as img:
            caption = f"{group} dars jadvali" if lang == "uz" else f"Расписание для {group}"
            bot.send_photo(chat_id, img, caption=caption)
    except FileNotFoundError:
        text = "Dars jadvali mavjud emas." if lang == "uz" else "Расписание не найдено."
        bot.send_message(chat_id, text)
    
    user_stage.pop(chat_id, None)
    user_class.pop(chat_id, None)
    bot.send_message(chat_id, "Boshqa savollar?" if lang == "uz" else "Ещё вопросы?", reply_markup=get_student_menu(lang))

# ============================================================
# STUDENT: BOSHQALAR UCHUN "TEZ ORADA"
# ============================================================
@bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "student" and 
                     m.text in ["ChSB demo", "ЧСБ демо", "IQ savollar", "IQ вопросы", 
                                "Fan testlari", "Тесты по предметам", "SAT misollari", "SAT задачи"])
def student_other(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = "Bu funksiya tez orada paydo bo‘ladi!" if lang == "uz" else "Эта функция скоро появится!"
    bot.send_message(chat_id, text)

# ============================================================
#   O‘QITUVCHI BO‘LIMI — YILLIK DARS REJASI
# ============================================================

@bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "teacher" and 
                     m.text in ["Sinflar uchun yillik dars rejasi", "Годовой план занятий"])
def teacher_start_plan(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    teacher_mode[chat_id] = True
    teacher_step[chat_id] = "class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    classes = ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]
    for c in classes:
        if lang == "ru":
            markup.add(c.replace("-sinf", "-класс"))
        else:
            markup.add(c)

    cancel_markup = teacher_cancel_buttons(lang)
    for row in cancel_markup.keyboard:
        markup.keyboard.append(row)

    text = "Выберите класс:" if lang == "ru" else "Siz qaysi sinfning rejasini bilmoqchisiz?"
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
#   2-QADAM – GURUH TANLASH
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id, False) and 
                     teacher_step.get(m.chat.id) == "class")
def teacher_choose_group(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = message.text.strip()

    sinf = None
    if "-sinf" in text:
        sinf = text.replace("-sinf", "")
    elif "-класс" in text:
        sinf = text.replace("-класс", "")
    
    if not sinf or sinf not in groups:
        return

    teacher_class[chat_id] = sinf
    teacher_step[chat_id] = "group"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for g in groups[sinf]:
        markup.add(g)

    cancel_markup = teacher_cancel_buttons(lang)
    for row in cancel_markup.keyboard:
        markup.keyboard.append(row)

    text = "Выберите параллель:" if lang == "ru" else "Qaysi guruhni tanlaysiz?"
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
#   3-QADAM – FANLAR TANLASH
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id, False) and 
                     teacher_step.get(m.chat.id) == "group")
def teacher_choose_subject(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = message.text.strip()

    all_groups = [g for sublist in groups.values() for g in sublist]
    if text not in all_groups:
        return

    teacher_group[chat_id] = text
    teacher_step[chat_id] = "subject"

    sinf = teacher_class.get(chat_id)
    sinf_int = int(sinf)

    subjects = subjects_ru["<7"] if (lang == "ru" and sinf_int < 7) else \
               subjects_uz["<7"] if (lang == "uz" and sinf_int < 7) else \
               subjects_ru[">=7"] if lang == "ru" else subjects_uz[">=7"]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for s in subjects:
        markup.add(s)

    missing_btn = missing_subject_ru if lang == "ru" else missing_subject_uz
    markup.add(missing_btn)

    cancel_markup = teacher_cancel_buttons(lang)
    for row in cancel_markup.keyboard:
        markup.keyboard.append(row)

    text = "Выберите предмет:" if lang == "ru" else "Qaysi fan rejasi kerak?"
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
#   KERAKLI FAN YO'Q HANDLERI
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id, False) and 
                     m.text in [missing_subject_uz, missing_subject_ru])
def teacher_missing_subject(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    
    text = "Sizga kerakli fan bu ro'yhatda bo'lmasa, u tez kunlarda qo'shiladi!" if lang == "uz" else "Если нужного предмета нет в списке, он будет добавлен в ближайшее время!"
    bot.send_message(chat_id, text)
    
    teacher_cancel(message)

# ============================================================
#   4-QADAM – FAN TANLANGANIDA NATIJA
# ============================================================

@bot.message_handler(func=lambda m: teacher_mode.get(m.chat.id, False) and 
                     teacher_step.get(m.chat.id) == "subject")
def teacher_subject_result(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    subject = message.text
    
    if subject in [missing_subject_uz, missing_subject_ru, "Bekor qilish", "Отмена", "Bosh menyu", "Главное меню"]:
        return

    sinf = teacher_class.get(chat_id)
    group = teacher_group.get(chat_id)
    
    text = f"{sinf}-{group} sinf uchun *{subject}* fanidan yillik dars rejasi tez orada qo‘shiladi!" if lang == "uz" else f"Годовой план по *{subject}* для {sinf}-{group} класса будет добавлен в ближайшее время!"
    bot.send_message(chat_id, text, parse_mode="Markdown")
    
    teacher_cancel(message)

# ============================================================
# CALLBACK → SHAXSIY TELEGRAM LINK
# ============================================================
@bot.message_handler(commands=['callback'])
def send_test(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Agar bot haqida e’tirozlaringiz bo‘lsa pastdagi tugmani bosing", reply_markup=get_feedback_inline())

# ============================================================
# UNIVERSAL RESTART – HAR QANDAY HOSTINGDA ISHLAYDI
# ============================================================

@bot.message_handler(commands=['restart'])
def universal_restart(message):
    bot.reply_to(message, "Bot qayta ishga tushirilmoqda...")
    print(f"[RESTART] {message.from_user.first_name} ({message.from_user.id}) botni restart qildi!")
    threading.Thread(target=os._exit, args=(0,)).start()

# ============================================================
# BOT2 NI ULASH — ENDI XAVFSIZ (eng oxirda!)
# ============================================================
from bot2 import register_handlers
register_handlers(bot, get_user, groups)

# ============================================================
# BOT ISHGA TUSHIRISH
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