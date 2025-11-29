import os
import sys
import telebot
from telebot import types
from tinydb import TinyDB, Query
import threading

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

db = TinyDB('users.json')
User = Query()

def get_user(chat_id):
    u = db.get(User.chat_id == chat_id)
    return u if u else {}

def save_user(chat_id, data: dict):
    u = get_user(chat_id)
    if not u:
        data["chat_id"] = chat_id
        db.insert(data)
    else:
        u.update(data)
        db.update(u, User.chat_id == chat_id)


PHONE_DATABASE = {
    "+998901234567": {"ism": "Test User 1"},
    "+998997654321": {"ism": "Test User 2"},
}

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
    "<7": ["Математика", "Английский язык", "Русский язык", "Родной язык",
           "История", "Литература", "География", "Биология"],
    ">=7": ["Алгебра", "Геометрия", "Английский язык", "Русский язык",
            "Родной язык", "История Узбекистана", "Всемирная история",
            "Литература", "География", "Биология", "Физика"]
}

missing_subject_uz = "Menga kerakli fan yo‘q ❗"
missing_subject_ru = "Нужного предмета нет ❗"


# ========================= MENU FUNKSIYALAR =========================

def get_role_menu(lang):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "ru":
        m.add("Ученик 👨‍🎓", "Учитель 👩‍🏫")
    else:
        m.add("O‘quvchi 👨‍🎓", "O‘qituvchi 👩‍🏫")
    m.add("1 qadam ortga ⬅️")
    return m


def get_student_menu(lang):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "ru":
        m.add("Расписание уроков 📑", "Тесты по предметам 🔖")
        m.add("ЧСБ демо 📝", "IQ вопросы 🧠")
        m.add("SAT задачи 📘", "Я не ученик")
    else:
        m.add("Dars jadvali 📑", "Fan testlari 🔖")
        m.add("ChSB demo 📝", "IQ savollar 🧠")
        m.add("SAT misollari 📘", "Men o‘quvchi emasman")
    m.add("1 qadam ortga ⬅️")
    return m


def get_teacher_menu(lang):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "ru":
        m.add("Годовой план занятий 📘")
    else:
        m.add("Sinflar uchun yillik dars rejasi 📘")
    m.add("1 qadam ortga ⬅️")
    return m


def get_class_menu(lang):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    arr = ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]
    for c in arr:
        if lang == "ru":
            m.add(c.replace("-sinf", "-класс"))
        else:
            m.add(c)
    m.add("1 qadam ortga ⬅️")
    return m


def get_subject_menu(lang, sinf_int):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)

    subs = (
        subjects_ru["<7"] if lang == "ru" and sinf_int < 7 else
        subjects_uz["<7"] if lang == "uz" and sinf_int < 7 else
        subjects_ru[">=7"] if lang == "ru" else
        subjects_uz[">=7"]
    )

    for s in subs:
        m.add(s)

    m.add(missing_subject_ru if lang == "ru" else missing_subject_uz)
    m.add("1 qadam ortga ⬅️")

    return m


# ========================= START =========================

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    u = get_user(chat_id)

    if u and u.get("registered"):
        send_role_menu(chat_id)
        return

    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("🇺🇿 O‘zbekcha", "🇷🇺 Русский")

    bot.send_message(chat_id, "Tilni tanlang:", reply_markup=m)
    save_user(chat_id, {"stage": "choose_lang"})


# ===================== TIL TANLASH =====================

@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "choose_lang")
def choose_lang(message):
    chat_id = message.chat.id
    if message.text == "🇺🇿 O‘zbekcha":
        lang = "uz"
    elif message.text == "🇷🇺 Русский":
        lang = "ru"
    else:
        return

    save_user(chat_id, {"lang": lang, "stage": "ask_contact"})

    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton(
        "Kontakt yuborish 📱" if lang == "uz" else "Отправить контакт 📱",
        request_contact=True
    )
    m.add(btn)

    bot.send_message(chat_id,
        "Telefon raqamingizni yuboring:" if lang == "uz" else "Отправьте номер телефона:",
        reply_markup=m
    )


# ===================== KONTAKT =====================

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    chat_id = message.chat.id
    u = get_user(chat_id)
    lang = u.get("lang", "uz")

    phone = message.contact.phone_number
    save_user(chat_id, {"phone": phone})

    if phone in PHONE_DATABASE:
        ism = PHONE_DATABASE[phone]["ism"]
        save_user(chat_id, {"registered": True, "full_name": ism, "stage": "choose_role"})

        bot.send_message(chat_id,
            "Kirdingiz!" if lang == "uz" else "Вы вошли!",
            reply_markup=types.ReplyKeyboardRemove()
        )
        send_role_menu(chat_id)
    else:
        save_user(chat_id, {"stage": "ask_name"})
        bot.send_message(chat_id,
            "Ism-familyangizni yozing:" if lang == "uz" else "Введите ФИО:",
            reply_markup=types.ForceReply()
        )


# ===================== ISM =====================

@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "ask_name")
def handle_name(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    save_user(chat_id, {
        "registered": True,
        "full_name": message.text.strip(),
        "stage": "choose_role"
    })

    bot.send_message(chat_id,
        "Ro‘yxatdan o‘tdingiz!" if lang == "uz" else "Вы зарегистрированы!",
        reply_markup=types.ReplyKeyboardRemove()
    )

    send_role_menu(chat_id)


# ===================== ROL =====================

def send_role_menu(chat_id):
    lang = get_user(chat_id).get("lang", "uz")
    bot.send_message(
        chat_id,
        "Rolni tanlang:" if lang == "uz" else "Выберите роль:",
        reply_markup=get_role_menu(lang)
    )


@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "choose_role")
def choose_role(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")
    txt = message.text

    if txt in ["O‘quvchi 👨‍🎓", "Ученик 👨‍🎓"]:
        save_user(chat_id, {"role": "student", "stage": "student_menu"})
        send_student_menu(chat_id)

    elif txt in ["O‘qituvchi 👩‍🏫", "Учитель 👩‍🏫"]:
        save_user(chat_id, {"role": "teacher", "stage": "teacher_menu"})
        send_teacher_menu(chat_id)


# ===================== O‘QUVCHI MENYUSI =====================

def send_student_menu(chat_id):
    lang = get_user(chat_id).get("lang", "uz")
    bot.send_message(
        chat_id,
        "Menyudan birini tanlang:" if lang == "uz" else "Выберите пункт меню:",
        reply_markup=get_student_menu(lang)
    )
    save_user(chat_id, {"stage": "student_menu"})


# ===================== DARS JADVALI =====================

@bot.message_handler(func=lambda m: get_user(m.chat.id).get("role") == "student"
                     and m.text in ["Dars jadvali 📑", "Расписание уроков 📑"])
def ask_class(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    save_user(chat_id, {"stage": "choose_class"})

    bot.send_message(
        chat_id,
        "Sinfni tanlang:" if lang == "uz" else "Выберите класс:",
        reply_markup=get_class_menu(lang)
    )


@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "choose_class")
def choose_group_student(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    t = message.text
    sinf = None

    if "-sinf" in t:
        sinf = t.replace("-sinf", "")
    if "-класс" in t:
        sinf = t.replace("-класс", "")

    if not sinf or sinf not in groups:
        return

    save_user(chat_id, {"class": sinf, "stage": "choose_group"})

    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[sinf]:
        m.add(g)
    m.add("1 qadam ortga ⬅️")

    bot.send_message(
        chat_id,
        "Guruhni tanlang:" if lang == "uz" else "Выберите группу:",
        reply_markup=m
    )


@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "choose_group")
def send_schedule(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    group = message.text
    path = f"images/{group}.jpg"

    try:
        with open(path, "rb") as img:
            cap = f"{group} dars jadvali 📘" if lang == "uz" else f"Расписание для {group} 📘"
            bot.send_photo(chat_id, img, caption=cap)
    except:
        bot.send_message(chat_id,
            "Dars jadvali topilmadi." if lang == "uz" else "Расписание не найдено."
        )

    send_student_menu(chat_id)


# ===================== TEST BO‘LIMLARI =====================

@bot.message_handler(func=lambda m: get_user(m.chat.id).get("role") == "student"
                     and m.text in ["Fan testlari 🔖", "Тесты по предметам 🔖"])
def testlar(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "uz":
        m.add("Qiziqquvchilar uchun testlar", "Olimpiada testlari")
    else:
        m.add("Тесты для интересующихся", "Тесты для олимпиад")
    m.add("1 qadam ortga ⬅️")

    save_user(chat_id, {"stage": "test_type"})

    bot.send_message(
        chat_id,
        "Test turini tanlang:" if lang == "uz" else "Выберите тип теста:",
        reply_markup=m
    )


@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "test_type")
def test_class(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    txt = message.text
    if txt not in [
        "Qiziqquvchilar uchun testlar", "Olimpiada testlari",
        "Тесты для интересующихся", "Тесты для олимпиад"
    ]:
        return

    save_user(chat_id, {"stage": "choose_class_test"})
    bot.send_message(
        chat_id,
        "Qaysi sinf darajasi?" if lang == "uz" else "Выберите класс:",
        reply_markup=get_class_menu(lang)
    )


@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "choose_class_test")
def test_subject(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    t = message.text
    sinf = None

    if "-sinf" in t:
        sinf = t.replace("-sinf", "")
    if "-класс" in t:
        sinf = t.replace("-класс", "")

    if not sinf or sinf not in groups:
        return

    save_user(chat_id, {"stage": "choose_subject_test", "class_test": sinf})

    bot.send_message(
        chat_id,
        "Qaysi fan?" if lang == "uz" else "Выберите предмет:",
        reply_markup=get_subject_menu(lang, int(sinf))
    )


@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "choose_subject_test")
def test_selected(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    bot.send_message(
        chat_id,
        "Bu fan bo‘yicha test tez orada tayyor bo‘ladi ⏳!" if lang == "uz"
        else "Тест по этому предмету скоро будет готов ⏳!"
    )

    send_student_menu(chat_id)


# ===================== MEN O‘QUVCHI EMASMAN =====================

@bot.message_handler(func=lambda m: m.text in ["Men o‘quvchi emasman", "Я не ученик"])
def not_student(message):
    chat_id = message.chat.id
    save_user(chat_id, {"stage": "choose_role"})
    send_role_menu(chat_id)


# ===================== 1 QADAM ORTGA =====================

@bot.message_handler(func=lambda m: m.text == "1 qadam ortga ⬅️")
def back(message):
    chat_id = message.chat.id
    u = get_user(chat_id)
    stage = u.get("stage")
    role = u.get("role")
    lang = u.get("lang", "uz")

    if stage == "student_menu":
        save_user(chat_id, {"stage": "choose_role"})
        send_role_menu(chat_id)
        return

    if stage in ["test_type", "choose_class_test", "choose_subject_test",
                 "choose_class", "choose_group"]:

        send_student_menu(chat_id)
        save_user(chat_id, {"stage": "student_menu"})
        return

    bot.send_message(chat_id,
        "Orqaga qaytish mumkin emas." if lang == "uz"
        else "Нельзя вернуться назад."
    )


# ===================== O‘QITUVCHI MENU =====================

def send_teacher_menu(chat_id):
    lang = get_user(chat_id).get("lang", "uz")
    bot.send_message(
        chat_id,
        "O‘qituvchilar menyusi:" if lang == "uz" else "Меню учителя:",
        reply_markup=get_teacher_menu(lang)
    )


# ===================== TEACHER → YEARLY PLAN =====================

@bot.message_handler(func=lambda m: get_user(m.chat.id).get("role") == "teacher"
                     and m.text in ["Sinflar uchun yillik dars rejasi 📘", "Годовой план занятий 📘"])
def teacher_start(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    save_user(chat_id, {"stage": "teacher_class"})

    bot.send_message(
        chat_id,
        "Sinfni tanlang:" if lang == "uz" else "Выберите класс:",
        reply_markup=get_class_menu(lang)
    )


@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "teacher_class")
def teacher_choose_group(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")

    t = message.text
    sinf = None

    if "-sinf" in t:
        sinf = t.replace("-sinf", "")
    if "-класс" in t:
        sinf = t.replace("-класс", "")

    if not sinf or sinf not in groups:
        return

    save_user(chat_id, {"stage": "teacher_group", "teacher_class": sinf})

    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[sinf]:
        m.add(g)
    m.add("1 qadam ortga ⬅️")

    bot.send_message(
        chat_id,
        "Guruhni tanlang:" if lang == "uz" else "Выберите группу:",
        reply_markup=m
    )


@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "teacher_group")
def teacher_choose_subject(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")
    group = message.text

    all_groups = sum(groups.values(), [])
    if group not in all_groups:
        return

    sinf = get_user(chat_id).get("teacher_class")
    save_user(chat_id, {"stage": "teacher_subject", "teacher_group": group})

    bot.send_message(
        chat_id,
        "Fan tanlang:" if lang == "uz" else "Выберите предмет:",
        reply_markup=get_subject_menu(lang, int(sinf))
    )


@bot.message_handler(func=lambda m: get_user(m.chat.id).get("stage") == "teacher_subject")
def teacher_subject_finish(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get("lang", "uz")
    subject = message.text

    sinf = get_user(chat_id).get("teacher_class")
    group = get_user(chat_id).get("teacher_group")

    if message.text in [missing_subject_uz, missing_subject_ru]:
        bot.send_message(chat_id,
            "Bu fan tez orada qo‘shiladi ⏳!" if lang == "uz"
            else "Этот предмет скоро будет добавлен ⏳!"
        )
    else:
        bot.send_message(
            chat_id,
            f"{sinf}-{group} uchun {subject} bo‘yicha YILLIK REJA tez orada qo‘shiladi ⏳!"
            if lang == "uz"
            else f"Годовой план по предмету {subject} для {sinf}-{group} скоро будет готов ⏳!"
        )

    send_teacher_menu(chat_id)
    save_user(chat_id, {"stage": "teacher_menu"})


# ===================== CALLBACK → E'TIROZ YUBORISH =====================

@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call):
    bot.answer_callback_query(call.id)
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("E'tiroz yuborish ✍🏼", url="https://t.me/khakimovvd")
    keyboard.add(btn)
    bot.send_message(call.message.chat.id, "E'tirozingizni yuborishingiz mumkin:", reply_markup=keyboard)


# ===================== RESTART =====================

@bot.message_handler(commands=['restart'])
def restart(message):
    bot.reply_to(message, "Bot qayta ishga tushmoqda...")
    threading.Thread(target=lambda: os._exit(0)).start()


# ===================== RUN =====================

if __name__ == "__main__":
    print("BOT ISHLAMOQDA...")
    bot.infinity_polling(skip_pending=True)

bot.infinity_polling()