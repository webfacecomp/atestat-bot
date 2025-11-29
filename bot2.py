# ============================================================
# bot2.py — Testlar + O‘qituvchi bo‘limi (2025-yil versiyasi)
# Circular import YO‘Q, Railway’da 100 % ishlaydi
# ============================================================

from telebot import types
# bot2.py ning eng yuqorisiga (from telebot import types dan keyin)
from bot import get_user, groups

# STATE STORAGE (har bir foydalanuvchi uchun alohida)
test_mode = {}
test_step = {}
test_class = {}

teacher_mode = {}
teacher_step = {}
teacher_class = {}
teacher_group = {}


# ============================================================
# FANLAR RO‘YXATI
# ============================================================
def get_subjects_for_class(sinf):
    sinf = int(sinf)
    if sinf < 7:
        return [
            "Matematika", "Inglis tili", "Rus tili", "Ona tili",
            "Tarix", "Adabiyot", "Geografiya", "Biologiya"
        ]
    else:
        return [
            "Algebra", "Geometriya", "Inglis tili", "Rus tili", "Ona tili",
            "O‘zbekiston tarixi", "Jahon tarixi", "Adabiyot",
            "Geografiya", "Biologiya", "Fizika"
        ]


# ============================================================
# TEST BO‘LIMI (O‘QUVCHI)
# ============================================================
def student_test_menu(bot, message):
    user = get_user(message.chat.id)          # <— bu funksiya bot.py da bor
    if not user:
        return
    lang = user.get('lang', 'uz')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("Qiziquvchilar uchun testlar", "Olimpiada testlar")
    markup.add("Ortga")

    bot.send_message(message.chat.id,
                     "Test turini tanlang:" if lang == "uz" else "Выберите тип теста:",
                     reply_markup=markup)


def handle_test_entry(bot, message):
    user = get_user(message.chat.id)
    if not user:
        return
    lang = user.get('lang', 'uz')
    chat_id = message.chat.id

    test_mode[chat_id] = True
    test_step[chat_id] = "choose_level"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for s in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(s)
    markup.add("Ortga")

    bot.send_message(chat_id,
                     "Sinf darajasini tanlang:" if lang == "uz" else "Выберите уровень:",
                     reply_markup=markup)


def handle_test_level(bot, message):
    if not message.text or not message.text.endswith("-sinf"):
        return

    chat_id = message.chat.id
    user = get_user(chat_id)
    if not user:
        return
    lang = user.get('lang', 'uz')

    sinf = message.text.replace("-sinf", "").strip()
    test_class[chat_id] = sinf
    test_step[chat_id] = "choose_subject"

    subjects = get_subjects_for_class(sinf)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for f in subjects:
        markup.add(f)
    markup.add("Menga kerakli fan yo‘q")
    markup.add("Ortga")

    bot.send_message(chat_id,
                     "Endi fanni tanlang:" if lang == "uz" else "Выберите предмет:",
                     reply_markup=markup)


def handle_test_subject(bot, message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    if not user:
        return
    lang = user.get('lang', 'uz')

    subject = message.text

    if subject == "Menga kerakli fan yo‘q":
        bot.send_message(chat_id, "Bu fan tez orada qo‘shiladi!")
        del test_mode[chat_id]
        return

    sinf = test_class.get(chat_id, "?")
    bot.send_message(chat_id,
                     f"{sinf}-sinf {subject} fanidan testlar tez orada paydo bo‘ladi!")

    # tozalash
    test_mode.pop(chat_id, None)
    test_step.pop(chat_id, None)
    test_class.pop(chat_id, None)


# ============================================================
# O‘QITUVCHI — YILLIK REJA
# ============================================================
def teacher_start(bot, message):
    user = get_user(message.chat.id)
    if not user:
        return
    lang = user.get('lang', 'uz')
    chat_id = message.chat.id

    teacher_mode[chat_id] = True
    teacher_step[chat_id] = "class"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for c in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(c)
    markup.add("Ortga")

    bot.send_message(chat_id, "Siz qaysi sinfni tanlaysiz?", reply_markup=markup)


def teacher_choose_class(bot, message):
    if not message.text.endswith("-sinf"):
        return

    chat_id = message.chat.id
    sinf = message.text.replace("-sinf", "").strip()
    teacher_class[chat_id] = sinf
    teacher_step[chat_id] = "group"

    # groups o‘zgaruvchisi bot.py da bor
    try:
        from bot import groups  # faqat shu joyda import qilamiz
    except ImportError:
        bot.send_message(chat_id, "Guruhlar ro‘yxati topilmadi.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for g in groups.get(sinf, []):
        markup.add(g)
    markup.add("Ortga")

    bot.send_message(chat_id, "Qaysi guruh?", reply_markup=markup)


def teacher_choose_group(bot, message):
    chat_id = message.chat.id
    group = message.text.strip()

    try:
        from bot import groups
    except ImportError:
        return

    if group not in sum(groups.values(), []):
        return

    teacher_group[chat_id] = group
    teacher_step[chat_id] = "subject"

    sinf = teacher_class.get(chat_id)
    subjects = get_subjects_for_class(sinf)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for s in subjects:
        markup.add(s)
    markup.add("Menga kerakli fan yo‘q")
    markup.add("Ortga")

    bot.send_message(chat_id, "Qaysi fan kerak?", reply_markup=markup)


def teacher_subject(bot, message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    if not user:
        return
    lang = user.get('lang', 'uz')

    subject = message.text

    if subject == "Menga kerakli fan yo‘q":
        bot.send_message(chat_id, "Bu fan tez orada qo‘shiladi!")
    else:
        sinf = teacher_class.get(chat_id, "?")
        group = teacher_group.get(chat_id, "?")
        bot.send_message(chat_id,
                         f"{sinf}-{group} uchun {subject} fanidan yillik reja tez orada qo‘shiladi!")

    # tozalash
    for d in [teacher_mode, teacher_step, teacher_class, teacher_group]:
        d.pop(chat_id, None)


# ============================================================
# HANDLERLAR — ENDI HECH QANDAY IMPORT YO‘Q!
# ============================================================
def register_handlers(bot):
    # O‘quvchi testlari
    @bot.message_handler(func=lambda m: get_user(m.chat.id).get('role') == 'student' and m.text == "Fan testlar")
    def show_test_menu(message):
        student_test_menu(bot, message)

    @bot.message_handler(func=lambda m: m.text in ["Qiziquvchilar uchun testlar", "Olimpiada testlar"])
    def test_start(message):
        handle_test_entry(bot, message)

    @bot.message_handler(func=lambda m: test_mode.get(m.chat.id) and test_step.get(m.chat.id) == "choose_level")
    def test_level(message):
        handle_test_level(bot, message)

    @bot.message_handler(func=lambda m: test_step.get(m.chat.id) == "choose_subject")
    def test_subject(message):
        handle_test_subject(bot, message)

    # O‘qituvchi yillik reja
    @bot.message_handler(func=lambda m: get_user(m.chat.id).get('role') == 'teacher' and m.text == "Sinflar uchun yillik dars rejasi")
    def teacher_plan_start(message):
        teacher_start(bot, message)

    @bot.message_handler(func=lambda m: teacher_step.get(m.chat.id) == "class")
    def t_class(message):
        teacher_choose_class(bot, message)

    @bot.message_handler(func=lambda m: teacher_step.get(m.chat.id) == "group")
    def t_group(message):
        teacher_choose_group(bot, message)

    @bot.message_handler(func=lambda m: teacher_step.get(m.chat.id) == "subject")
    def t_subject(message):
        teacher_subject(bot, message)
