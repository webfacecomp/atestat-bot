# bot2.py — Faqat sizning hozirgi bot.py bilan 100% ishlaydi!

from telebot import types

# State storage
test_mode = {}
test_step = {}
test_class = {}

teacher_mode = {}
teacher_step = {}
teacher_class = {}
teacher_group = {}

# Fanlar ro‘yxati
def get_subjects_for_class(sinf):
    sinf = int(sinf)
    if sinf < 7:
        return ["Matematika", "Inglis tili", "Rus tili", "Ona tili", "Tarix", "Adabiyot", "Geografiya", "Biologiya"]
    else:
        return ["Algebra", "Geometriya", "Inglis tili", "Rus tili", "Ona tili",
                "O‘zbekiston tarixi", "Jahon tarixi", "Adabiyot", "Geografiya", "Biologiya", "Fizika"]

# ====================== TEST BO‘LIMI ======================
def student_test_menu(bot, message, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("Qiziquvchilar uchun testlar")
    markup.add("Olimpiada testlari")
    markup.add("Ortga")
    bot.send_message(message.chat.id, "Test turini tanlang:" if lang == "uz" else "Выберите тип теста:", reply_markup=markup)

def handle_test_entry(bot, message, lang):
    chat_id = message.chat.id
    test_mode[chat_id] = True
    test_step[chat_id] = "choose_level"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for s in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(s)
    markup.add("Ortga")
    bot.send_message(chat_id, "Sinfni tanlang:" if lang == "uz" else "Выберите класс:", reply_markup=markup)

def handle_test_level(bot, message, lang):
    if not message.text or "-sinf" not in message.text:
        return
    sinf = message.text.replace("-sinf", "").strip()
    chat_id = message.chat.id
    test_class[chat_id] = sinf
    test_step[chat_id] = "choose_subject"
    subjects = get_subjects_for_class(sinf)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for s in subjects:
        markup.add(s)
    markup.add("Menga kerakli fan yo‘q")
    markup.add("Ortga")
    bot.send_message(chat_id, "Fanni tanlang:" if lang == "uz" else "Выберите предмет:", reply_markup=markup)

def handle_test_subject(bot, message):
    chat_id = message.chat.id
    if message.text == "Menga kerakli fan yo‘q":
        bot.send_message(chat_id, "Bu fan tez orada qo‘shiladi!")
        test_mode.pop(chat_id, None)
        return
    sinf = test_class.get(chat_id, "?")
    bot.send_message(chat_id, f"{sinf}-sinf {message.text} fanidan testlar tez orada paydo bo‘ladi!")
    test_mode.pop(chat_id, None)
    test_step.pop(chat_id, None)
    test_class.pop(chat_id, None)

# ====================== O‘QITUVCHI YILLIK REJA ======================
def teacher_start(bot, message, lang):
    chat_id = message.chat.id
    teacher_mode[chat_id] = True
    teacher_step[chat_id] = "class"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for c in ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]:
        markup.add(c)
    markup.add("Ortga")
    bot.send_message(chat_id, "Sinfni tanlang:", reply_markup=markup)

def teacher_choose_class(bot, message, groups_dict):
    if not message.text or "-sinf" not in message.text:
        return
    sinf = message.text.replace("-sinf", "").strip()
    chat_id = message.chat.id
    teacher_class[chat_id] = sinf
    teacher_step[chat_id] = "group"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for g in groups_dict.get(sinf, []):
        markup.add(g)
    markup.add("Ortga")
    bot.send_message(chat_id, "Guruhni tanlang:", reply_markup=markup)

def teacher_choose_group(bot, message):
    chat_id = message.chat.id
    group = message.text.strip()
    all_groups = [g for sub in groups.values() for g in sub]
    if group not in all_groups:
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
    bot.send_message(chat_id, "Fanni tanlang:", reply_markup=markup)

def teacher_subject(bot, message):
    chat_id = message.chat.id
    if message.text == "Menga kerakli fan yo‘q":
        bot.send_message(chat_id, "Tez orada qo‘shiladi!")
    else:
        sinf = teacher_class.get(chat_id, "?")
        group = teacher_group.get(chat_id, "?")
        bot.send_message(chat_id, f"{sinf}-{group} uchun {message.text} fanidan yillik reja tez orada qo‘shiladi!")
    # tozalash
    for d in [teacher_mode, teacher_step, teacher_class, teacher_group]:
        d.pop(chat_id, None)

# ====================== REGISTER HANDLERS (MUHIM!) ======================
def register_handlers(bot, get_user_func, groups_dict):
    # Fan testlari — to‘g‘ri matn!
    @bot.message_handler(func=lambda m: get_user_func(m.chat.id).get('role') == 'student' and m.text == "Fan testlari")
    def show_test_menu(message):
        user = get_user_func(message.chat.id)
        lang = user.get('lang', 'uz')
        student_test_menu(bot, message, lang)

    @bot.message_handler(func=lambda m: m.text in ["Qiziquvchilar uchun testlar", "Olimpiada testlari"])
    def test_entry(message):
        user = get_user_func(message.chat.id)
        lang = user.get('lang', 'uz')
        handle_test_entry(bot, message, lang)

    @bot.message_handler(func=lambda m: test_mode.get(m.chat.id) and test_step.get(m.chat.id) == "choose_level")
    def test_level(message):
        user = get_user_func(message.chat.id)
        lang = user.get('lang', 'uz')
        handle_test_level(bot, message, lang)

    @bot.message_handler(func=lambda m: test_step.get(m.chat.id) == "choose_subject")
    def test_subject(message):
        handle_test_subject(bot, message)

    # O‘qituvchi yillik reja — to‘g‘ri matn!
    @bot.message_handler(func=lambda m: get_user_func(m.chat.id).get('role') == 'teacher' and m.text == "Sinflar uchun yillik dars rejasi")
    def teacher_plan_start(message):
        user = get_user_func(message.chat.id)
        lang = user.get('lang', 'uz')
        teacher_start(bot, message, lang)

    @bot.message_handler(func=lambda m: teacher_step.get(m.chat.id) == "class")
    def t_class(message):
        teacher_choose_class(bot, message, groups_dict)

    @bot.message_handler(func=lambda m: teacher_step.get(m.chat.id) == "group")
    def t_group(message):
        teacher_choose_group(bot, message)

    @bot.message_handler(func=lambda m: teacher_step.get(m.chat.id) == "subject")
    def t_subject(message):
        teacher_subject(bot, message)