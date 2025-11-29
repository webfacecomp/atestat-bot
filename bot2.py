# ============================================================
# bot2.py — Qo‘shimcha funksiyalar moduli (TESTLAR + O‘QITUVCHI)
# ============================================================

from telebot import types

# ===== EXTERNAL VARIABLES (asosiy botdan import qilinadi) =====
# bot, user_role, user_lang, groups kabi o‘zgaruvchilar asosiy botda turadi.
# Asosiy faylda yoziladi:
#     from bot2 import register_handlers
#     register_handlers(bot)
# ===============================================================

# STATE STORAGE
student_step = {}
teacher_mode = {}
teacher_step = {}
teacher_class = {}
teacher_group = {}
test_mode = {}
test_step = {}
test_class = {}
test_subject = {}

# ============================================================
# ——— FANLAR RO‘YXATI FUNKSIYASI
# ============================================================

def get_subjects_for_class(sinf):
    """Sinfga qarab fanlar ro‘yxatini qaytaradi."""
    sinf = int(sinf)

    if sinf < 7:
        return [
            "Matematika",
            "Inglis tili",
            "Rus tili",
            "Ona tili",
            "Tarix",
            "Adabiyot",
            "Geografiya",
            "Biologiya"
        ]
    else:
        return [
            "Algebra",
            "Geometriya",
            "Inglis tili",
            "Rus tili",
            "Ona tili",
            "O‘zbekiston tarixi",
            "Jahon tarixi",
            "Adabiyot",
            "Geografiya",
            "Biologiya",
            "Fizika"
        ]


# ============================================================
# ——— TEST BO‘LIMI (O‘QUVCHI)
# ============================================================

def student_test_menu(bot, message, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Qiziquvchilar uchun testlar ⭐")
    markup.add("Olimpiada testlar 🏆")
    markup.add("⬅️ Ortga")

    bot.send_message(
        message.chat.id,
        "Test turini tanlang:" if lang == "uz" else "Выберите тип теста:",
        reply_markup=markup
    )


def handle_test_entry(bot, message, lang):
    chat_id = message.chat.id
    test_mode[chat_id] = True
    test_step[chat_id] = "choose_level"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for s in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(s)

    markup.add("⬅️ Ortga")

    bot.send_message(
        chat_id,
        "Sinf darajasini tanlang:" if lang == "uz" else "Выберите уровень:",
        reply_markup=markup
    )


def handle_test_level(bot, message, lang):
    chat_id = message.chat.id

    if not message.text.endswith("-sinf"):
        return

    sinf = message.text.replace("-sinf", "")
    test_class[chat_id] = sinf
    test_step[chat_id] = "choose_subject"

    subjects = get_subjects_for_class(sinf)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for f in subjects:
        markup.add(f)

    markup.add("Menga kerakli fan yo‘q ❗")
    markup.add("⬅️ Ortga")

    bot.send_message(
        chat_id,
        "Endi fanni tanlang:" if lang == "uz" else "Выберите предмет:",
        reply_markup=markup
    )


def handle_test_subject(bot, message):
    chat_id = message.chat.id
    subject = message.text

    if subject == "Menga kerakli fan yo‘q ❗":
        bot.send_message(chat_id, "Bu fan tez orada qo‘shiladi ⏳!")
        return

    sinf = test_class.get(chat_id)

    bot.send_message(
        chat_id,
        f"{sinf}-sinf uchun {subject} fanidan testlar tez orada qo‘shiladi ⏳!"
    )

    test_mode[chat_id] = False
    test_step[chat_id] = None


# ============================================================
# ——— O‘QITUVCHI BO‘LIMI — YILLIK REJA
# ============================================================

def teacher_start(bot, message, lang):
    chat_id = message.chat.id

    teacher_mode[chat_id] = True
    teacher_step[chat_id] = "class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(c)

    markup.add("⬅️ Ortga")

    bot.send_message(
        chat_id,
        "Siz qaysi sinfni tanlaysiz?",
        reply_markup=markup
    )


def teacher_choose_class(bot, message):
    chat_id = message.chat.id
    if not message.text.endswith("-sinf"):
        return

    sinf = message.text.replace("-sinf", "")
    teacher_class[chat_id] = sinf

    teacher_step[chat_id] = "group"

    # guruhlar asosiy botdan olinadi
    from main import groups

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[sinf]:
        markup.add(g)

    markup.add("⬅️ Ortga")

    bot.send_message(chat_id, "Qaysi guruh?", reply_markup=markup)


def teacher_choose_group(bot, message):
    chat_id = message.chat.id
    group = message.text

    from main import groups
    all_groups = sum(groups.values(), [])

    if group not in all_groups:
        return

    teacher_group[chat_id] = group
    teacher_step[chat_id] = "subject"

    sinf = teacher_class.get(chat_id)
    subjects = get_subjects_for_class(sinf)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for s in subjects:
        markup.add(s)

    markup.add("Menga kerakli fan yo‘q ❗")
    markup.add("⬅️ Ortga")

    bot.send_message(chat_id, "Qaysi fan kerak?", reply_markup=markup)


def teacher_subject(bot, message):
    chat_id = message.chat.id

    subject = message.text
    sinf = teacher_class.get(chat_id)
    group = teacher_group.get(chat_id)

    if subject == "Menga kerakli fan yo‘q ❗":
        bot.send_message(chat_id, "Bu fan tez orada qo‘shiladi ⏳!")
        return

    bot.send_message(
        chat_id,
        f"{sinf}-{group} uchun {subject} fanidan yillik reja tez orada qo‘shiladi ⏳!"
    )

    teacher_mode[chat_id] = False
    teacher_step[chat_id] = None


# ============================================================
# ——— HANDLERLARNI RO‘YXATGA OLISH
# ============================================================

def register_handlers(bot):
    # bot2.py ichida 237-qator atrofida
    from bot import user_role, user_lang

    # ========= TESTLAR MENYUSI =========
    @bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "student" and m.text == "Fan testlar 📝")
    def show_student_test_menu(message):
        student_test_menu(bot, message, user_lang.get(message.chat.id, "uz"))

    # ========= TEST TURI TANLANGANDA =========
    @bot.message_handler(func=lambda m: m.text in ["Qiziquvchilar uchun testlar ⭐", "Olimpiada testlar 🏆"])
    def test_level_choice(message):
        handle_test_entry(bot, message, user_lang.get(message.chat.id, "uz"))

    # ========= TEST SINF TANLANGANDA =========
    @bot.message_handler(func=lambda m: test_mode.get(m.chat.id) and test_step.get(m.chat.id) == "choose_level")
    def finish_test_level(message):
        handle_test_level(bot, message, user_lang.get(message.chat.id, "uz"))

    # ========= TEST FAN TANLANGANDA =========
    @bot.message_handler(func=lambda m: test_step.get(m.chat.id) == "choose_subject")
    def finish_test_subject(message):
        handle_test_subject(bot, message)

    # ========= O‘QITUVCHI — YILLIK REJA =========
    @bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "teacher" and m.text == "Sinflar uchun yillik dars rejasi 📘")
    def teacher_start_plan(message):
        teacher_start(bot, message, user_lang.get(message.chat.id, "uz"))

    @bot.message_handler(func=lambda m: teacher_step.get(m.chat.id) == "class")
    def teacher_class_select(message):
        teacher_choose_class(bot, message)

    @bot.message_handler(func=lambda m: teacher_step.get(m.chat.id) == "group")
    def teacher_group_select(message):
        teacher_choose_group(bot, message)

    @bot.message_handler(func=lambda m: teacher_step.get(m.chat.id) == "subject")
    def teacher_subject_select(message):
        teacher_subject(bot, message)

