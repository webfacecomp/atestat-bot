```python
import os
import telebot
from telebot import types
from fastapi import FastAPI, Request
from tinydb import TinyDB, Query
import threading

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ============================================================
# USER DATA - TinyDB bilan saqlash
# ============================================================
db = TinyDB('users.json')
User = Query()

# ============================================================
# PHONE DATABASE - O'quvchilar bazasida
# ============================================================
PHONE_DATABASE = {
    "+998901234567": {"ism": "Test User 1"},
    "+998997654321": {"ism": "Test User 2"},
    # O'zingiz qo'shing
}

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

missing_subject_uz = "Menga kerakli fan yo‘q ❗"
missing_subject_ru = "Нужного предмета нет ❗"

# ============================================================
# YORDAMCHI FUNKSIYALAR
# ============================================================

def teacher_cancel_buttons(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == "ru":
        markup.add("Отмена ↩️", "Главное меню ⏪")
    else:
        markup.add("Bekor qilish ↩️", "Bosh menyu ⏪")
    return markup

def get_role_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == "ru":
        markup.add("Ученик 👨‍🎓", "Учитель 👩‍🏫")
    else:
        markup.add("O‘quvchi 👨‍🎓", "O‘qituvchi 👩‍🏫")
    markup.add("1 qadam ortga ⬅️")
    return markup

def get_student_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == "ru":
        markup.add("Расписание уроков 📑", "Тесты по предметам 🔖")
        markup.add("ЧСБ демо 📝", "IQ вопросы 🧠")
        markup.add("SAT задачи 📘", "Я не ученик")
    else:
        markup.add("Dars jadvali 📑", "Fan testlari 🔖")
        markup.add("ChSB demo 📝", "IQ savollar 🧠")
        markup.add("SAT misollari 📘", "Men o‘quvchi emasman")
    markup.add("1 qadam ortga ⬅️")
    return markup

def get_test_type_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == "ru":
        markup.add("Тесты для интересующихся", "Тесты для олимпиад")
    else:
        markup.add("Qiziqquvchilar uchun testlar", "Olimpiada testlari")
    markup.add("1 qadam ortga ⬅️")
    return markup

def get_class_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    classes = ["5-sinf", "6-sinf", "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]
    for c in classes:
        if lang == "ru":
            ru_class = c.replace("-sinf", "-класс")
            markup.add(ru_class)
        else:
            markup.add(c)
    markup.add("1 qadam ortga ⬅️")
    return markup

def get_subject_menu(lang, sinf_int):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    subjects = subjects_ru["<7"] if (lang == "ru" and sinf_int < 7) else \
               subjects_uz["<7"] if (lang == "uz" and sinf_int < 7) else \
               subjects_ru[">=7"] if lang == "ru" else subjects_uz[">=7"]
    for s in subjects:
        markup.add(s)
    markup.add(missing_subject_ru if lang == "ru" else missing_subject_uz)
    markup.add("1 qadam ortga ⬅️")
    return markup

def get_feedback_inline():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text="E'tiroz yuborish ✍🏼", url="https://t.me/khakimovvd")
    keyboard.add(btn)
    return keyboard

# ============================================================
# /start — TIL TANLASH
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    
    if user and user.get('registered'):
        lang = user.get('lang', "uz")
        send_role_menu(chat_id)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("🇺🇿 O‘zbekcha", "🇷🇺 Русский")
        bot.send_message(chat_id, "Assalomu aleykum! Men sizni korganimdan hursandman. Siz qaysi tilda suhbatlashmoqchisiz?", reply_markup=markup)
        save_user(chat_id, {'stage': 'choose_lang'})

# ============================================================
# TIL TANLANDI → LOGIN/ROYHATDAN OTISH
# ============================================================
@bot.message_handler(func=lambda m: get_user(m.chat.id).get('stage') == 'choose_lang' and m.text in ["🇺🇿 O‘zbekcha", "🇷🇺 Русский"])
def choose_lang(message):
    chat_id = message.chat.id
    lang = "uz" if "O‘zbekcha" in message.text else "ru"
    save_user(chat_id, {'lang': lang, 'stage': 'ask_contact'})
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("Kontakt yuborish 📱" if lang == "uz" else "Отправить контакт 📱", request_contact=True)
    markup.add(btn)
    
    text = "Login yoki ro‘yxatdan o‘tish uchun telefon raqamingizni yuboring" if lang == "uz" else "Для входа или регистрации отправьте номер телефона"
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# KONTAKT KELDI → TEKSHIRISH
# ============================================================
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    if not user:
        return
    
    lang = user.get('lang', "uz")
    phone = message.contact.phone_number
    
    save_user(chat_id, {'phone': phone})
    
    # Bazada borligini tekshirish
    if phone in PHONE_DATABASE:
        ism = PHONE_DATABASE[phone].get('ism', "Noma'lum")
        save_user(chat_id, {'registered': True, 'full_name': ism, 'stage': 'choose_role'})
        text = "Muvaffaqiyatli kirdingiz!" if lang == "uz" else "Успешный вход!"
        bot.send_message(chat_id, text, reply_markup=types.ReplyKeyboardRemove())
        send_role_menu(chat_id)
    else:
        # Birinchi marta – ism-familya so‘raymiz
        save_user(chat_id, {'stage': 'ask_name'})
        markup = types.ForceReply(selective=False)
        text = "Birinchi marta ro‘yxatdan o‘tyapsiz. Ism-familyangizni yozing:" if lang == "uz" else "Первый раз регистрируетесь. Введите ФИО:"
        bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# ISM-FAMILYA KELDI → RO'YXATDAN O'TISH
# ============================================================
@bot.message_handler(func=lambda m: get_user(m.chat.id).get('stage') == 'ask_name')
def handle_name(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    lang = user.get('lang', "uz")
    full_name = message.text.strip()
    
    save_user(chat_id, {'registered': True, 'full_name': full_name, 'stage': 'choose_role'})
    
    text = f"Rahmat, {full_name}! Ro‘yxatdan o‘tdingiz." if lang == "uz" else f"Спасибо, {full_name}! Вы зарегистрированы."
    bot.send_message(chat_id, text, reply_markup=types.ReplyKeyboardRemove())
    send_role_menu(chat_id)

# ============================================================
# ROL TANLASH
# ============================================================
def send_role_menu(chat_id):
    user = get_user(chat_id)
    lang = user.get('lang', "uz")
    markup = get_role_menu(lang)
    bot.send_message(chat_id, "Siz qaysi rolda foydalanasiz?" if lang == "uz" else "В какой роли вы будете использовать?", reply_markup=markup)

@bot.message_handler(func=lambda m: get_user(m.chat.id).get('stage') == 'choose_role' and m.text in ["O‘quvchi 👨‍🎓", "O‘qituvchi 👩‍🏫", "Ученик 👨‍🎓", "Учитель 👩‍🏫"])
def handle_role(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    lang = user.get('lang', "uz")
    
    role = "student" if "O‘quvchi" in message.text or "Ученик" in message.text else "teacher"
    save_user(chat_id, {'role': role, 'stage': 'main_menu'})
    
    if role == "student":
        send_student_menu(chat_id)
    else:
        send_teacher_menu(chat_id)

# ============================================================
# O'QUVCHI MENYUSI
# ============================================================
def send_student_menu(chat_id):
    user = get_user(chat_id)
    lang = user.get('lang', "uz")
    markup = get_student_menu(lang)
    bot.send_message(chat_id, "Quyidagilardan birini tanlang:" if lang == "uz" else "Выберите один из вариантов:", reply_markup=markup)
    save_user(chat_id, {'stage': 'student_menu'})

# ============================================================
# DARS JADVALI (O'ZGARMADI)
# ============================================================
@bot.message_handler(func=lambda m: get_user(m.chat.id).get('role') == "student" and m.text in ["Dars jadvali 📑", "Расписание уроков 📑"])
def ask_class(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get('lang', "uz")
    save_user(chat_id, {'stage': 'choose_class'})
    
    markup = get_class_menu(lang)
    text = "Siz qaysi sinfning rejasini bilmoqchisiz?" if lang == "uz" else "Выберите класс:"
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(func=lambda m: get_user(m.chat.id).get('stage') == 'choose_class')
def choose_group_student(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get('lang', "uz")
    text = message.text.strip()
    
    sinf = None
    if "-sinf" in text:
        sinf = text.replace("-sinf", "")
    elif "-класс" in text:
        sinf = text.replace("-класс", "")
    
    if not sinf or sinf not in groups:
        return
    
    save_user(chat_id, {'class': sinf, 'stage': 'choose_group'})
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for g in groups[sinf]:
        markup.add(g)
    markup.add("1 qadam ortga ⬅️")
    text = "Qaysi guruhni tanlaysiz?" if lang == "uz" else "Выберите группу:"
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(func=lambda m: get_user(m.chat.id).get('stage') == 'choose_group')
def send_schedule(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get('lang', "uz")
    group = message.text
    
    path = f"images/{group}.jpg"
    
    try:
        with open(path, "rb") as img:
            caption = f"{group} dars jadvali 📚" if lang == "uz" else f"Расписание для {group} 📚"
            bot.send_photo(chat_id, img, caption=caption)
    except FileNotFoundError:
        text = "Dars jadvali mavjud emas." if lang == "uz" else "Расписание не найдено."
        bot.send_message(chat_id, text)
    
    # Holatni tozalash va menyuga qaytish
    save_user(chat_id, {'stage': 'student_menu'})
    send_student_menu(chat_id)

# ============================================================
# FAN TESTLARI
# ============================================================
@bot.message_handler(func=lambda m: get_user(m.chat.id).get('role') == "student" and m.text in ["Fan testlari 🔖", "Тесты по предметам 🔖"])
def handle_fan_testlar(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get('lang', "uz")
    save_user(chat_id, {'stage': 'test_type'})
    
    markup = get_test_type_menu(lang)
    text = "Test turini tanlang:" if lang == "uz" else "Выберите тип теста:"
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# TEST TURI TANLANDI → SINF SO'RAYDI
# ============================================================
@bot.message_handler(func=lambda m: get_user(m.chat.id).get('stage') == 'test_type' and m.text in ["Qiziqquvchilar uchun testlar", "Olimpiada testlari", "Тесты для интересующихся", "Тесты для олимпиад"])
def handle_test_type(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    lang = user.get('lang', "uz")
    test_type = "qiziq" if "Qiziqquvchilar" in message.text or "интересующихся" in message.text else "olimpiada"
    save_user(chat_id, {'test_type': test_type, 'stage': 'choose_class_test'})
    
    markup = get_class_menu(lang)
    text = "Siz qaysi darajada test ishlamoqchisiz?" if lang == "uz" else "Выберите уровень теста:"
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# SINF TANLANDI → FAN SO'RAYDI
# ============================================================
@bot.message_handler(func=lambda m: get_user(m.chat.id).get('stage') == 'choose_class_test')
def handle_class_test(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    lang = user.get('lang', "uz")
    text = message.text.strip()
    
    sinf = None
    if "-sinf" in text:
        sinf = text.replace("-sinf", "")
    elif "-класс" in text:
        sinf = text.replace("-класс", "")
    
    if not sinf or sinf not in groups:
        return
    
    sinf_int = int(sinf)
    save_user(chat_id, {'class_test': sinf, 'stage': 'choose_subject_test'})
    
    markup = get_subject_menu(lang, sinf_int)
    text = "Ana endi qaysi fandan test ishlamoqchisiz?" if lang == "uz" else "Теперь выберите предмет для теста:"
    bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# FAN TANLANDI → TEST BOSHLASH (hozircha placeholder)
# ============================================================
@bot.message_handler(func=lambda m: get_user(m.chat.id).get('stage') == 'choose_subject_test')
def handle_subject_test(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    lang = user.get('lang', "uz")
    subject = message.text
    
    # Hozircha "tez orada", keyin real test qo'shasiz
    text = "Bu fan bo'yicha test tez orada qo'shiladi ⏳!" if lang == "uz" else "Тест по этому предмету будет добавлен вскоре ⏳!"
    bot.send_message(chat_id, text)
    
    # Menyuga qaytish
    save_user(chat_id, {'stage': 'student_menu'})
    send_student_menu(chat_id)

# ============================================================
# 1 QADAM ORTGA TUGMALARI
# ============================================================
@bot.message_handler(func=lambda m: m.text == "1 qadam ortga ⬅️")
def handle_back(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    stage = user.get('stage')
    lang = user.get('lang', "uz")
    
    if stage == 'student_menu':
        send_role_menu(chat_id)
    elif stage == 'test_type':
        send_student_menu(chat_id)
    elif stage == 'choose_class_test':
        handle_fan_testlar(message)  # Test turiga qaytish
    elif stage == 'choose_subject_test':
        handle_test_type(message)  # Sinfga qaytish
    elif stage == 'choose_group':
        ask_class(message)  # Sinfga qaytish
    else:
        bot.send_message(chat_id, "Ortga qaytish mumkin emas" if lang == "uz" else "Нельзя вернуться назад")

# ============================================================
# O'QUVCHI BOSHQAGA
# ============================================================
@bot.message_handler(func=lambda m: get_user(m.chat.id).get('role') == "student" and m.text in ["ChSB demo 📝", "ЧСБ демо 📝", "IQ savollar 🧠", "IQ вопросы 🧠", "SAT misollari 📘", "SAT задачи 📘"])
def student_other(message):
    chat_id = message.chat.id
    lang = get_user(chat_id).get('lang', "uz")
    text = "Bu funksiya tez orada paydo bo‘ladi ⏳!" if lang == "uz" else "Эта функция скоро появится ⏳!"
    bot.send_message(chat_id, text)

# ============================================================
# "MEN O'QUVCHI EMASMAN" → ROLGA QAYTISH
# ============================================================
@bot.message_handler(func=lambda m: m.text in ["Men o‘quvchi emasman", "Я не ученик"])
def not_student(message):
    chat_id = message.chat.id
    save_user(chat_id, {'stage': 'choose_role'})
    send_role_menu(chat_id)

# ============================================================
# O'QITUVCHI BO'LIMI (O'ZGARMADI)
# ============================================================

# ... (oldingi o'qituvchi kodini shu yerga qo'ying, tegmaganman)

# ============================================================
# UNIVERSAL RESTART – HAR QANDAY HOSTINGDA ISHLAYDI
# ============================================================

@bot.message_handler(commands=['restart'])
def universal_restart(message):
    bot.reply_to(message, "Bot qayta ishga tushirilmoqda...")
    print(f"[RESTART] {message.from_user.first_name} ({message.from_user.id}) botni restart qildi!")

    # 1.5 soniya kutib, xabar yetib borishi uchun
    threading.Thread(target=lambda: (
        os._exit(0)
    )).start()

# ============================================================
# BOT START
# ============================================================
if __name__ == "__main__":
    print("Bot ishga tushdi...")
    try:
        bot.infinity_polling(none_stop=True, interval=0)
    except:
        print("Bot to‘xtadi, 5 soniyadan keyin qayta ishga tushadi...")
        import time
        time.sleep(5)
        os.execv(__file__, ['python'] + [__file__])
```
bot.infinity_polling()