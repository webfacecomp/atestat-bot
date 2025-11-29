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
user_firstname = {}
user_lastname = {}
user_logged_in = {}

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

missing_subject_uz = "Menga kerakli fan yo‘q ❗"
missing_subject_ru = "Нужного предмета нет ❗"

# ============================================================

# YORDAMCHI FUNKSIYALAR

# ============================================================

def cancel_button(lang):
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
if lang=="ru":
markup.add("Отмена ↩️")
else:
markup.add("Bekor qilish ↩️")
return markup

def back_menu(lang):
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
if lang=="ru":
markup.add("Главное меню ⏪")
else:
markup.add("Bosh menyu ⏪")
return markup

def get_teacher_menu(lang):
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
if lang=="ru":
markup.add("Годовой план занятий 📘")
else:
markup.add("Sinflar uchun yillik dars rejasi 📘")
return markup

def get_student_menu(lang):
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
if lang=="ru":
markup.add("Dars jadvali 📑")
markup.add("Fan testlari 🔖")
markup.add("ChSB demo 📝")
markup.add("IQ вопросы 🧠")
markup.add("SAT задачи 📘")
markup.add("Я не ученик")
else:
markup.add("Dars jadvali 📑")
markup.add("Fan testlari 🔖")
markup.add("ChSB demo 📝")
markup.add("IQ savollar 🧠")
markup.add("SAT misollari 📘")
markup.add("Men o‘quvchi emasman")
return markup

def get_test_types(lang):
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
if lang=="ru":
markup.add("Qiziquvchilar uchun testlar")
markup.add("Olimpiada testlar")
else:
markup.add("Qiziquvchilar uchun testlar")
markup.add("Olimpiada testlar")
markup.add("↩️ Orqaga")
return markup

def get_test_levels(lang):
markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
for i in range(5,12):
markup.add(str(i))
markup.add("↩️ Orqaga")
return markup

def get_feedback_inline():
keyboard = types.InlineKeyboardMarkup(row_width=1)
btn = types.InlineKeyboardButton(text="E'tiroz yuborish ✍🏼", url="[https://t.me/khakimovvd](https://t.me/khakimovvd)")
keyboard.add(btn)
return keyboard

# ============================================================

# /start - LANGUAGE SELECT

# ============================================================

@bot.message_handler(commands=["start"])
def start(message):
chat_id = message.chat.id
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add("Uzb 🇺🇿")
markup.add("Rus 🇷🇺")
bot.send_message(chat_id,"Assalomu aleykum! Siz qaysi tilda suhbatlashmoqchisiz?", reply_markup=markup)

# ============================================================

# LANGUAGE SELECTED → LOGIN/REGISTRATION

# ============================================================

@bot.message_handler(func=lambda m: m.text in ["Uzb 🇺🇿","Rus 🇷🇺"])
def choose_lang(message):
chat_id = message.chat.id
lang = "uz" if message.text=="Uzb 🇺🇿" else "ru"
user_lang[chat_id]=lang
bot.send_message(chat_id,"Iltimos, kontaktingizni yuboring, login yoki ro‘yxatdan o‘tish uchun.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Kontakt yuborish ☎️", request_contact=True)))
user_stage[chat_id]="login"

# ============================================================

# CONTACT HANDLER → NAME/FAMILY ASK

# ============================================================

@bot.message_handler(content_types=["contact"])
def contact_handler(message):
chat_id = message.chat.id
if user_stage.get(chat_id)=="login":
user_logged_in[chat_id]=True
if chat_id not in user_firstname:
bot.send_message(chat_id,"Iltimos, ismingizni kiriting:")
user_stage[chat_id]="ask_firstname"
else:
bot.send_message(chat_id,"Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!", reply_markup=get_student_menu(user_lang[chat_id]))
user_stage[chat_id]=None

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="ask_firstname")
def ask_firstname(message):
chat_id = message.chat.id
user_firstname[chat_id]=message.text
bot.send_message(chat_id,"Endi familiyangizni kiriting:")
user_stage[chat_id]="ask_lastname"

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="ask_lastname")
def ask_lastname(message):
chat_id = message.chat.id
user_lastname[chat_id]=message.text
bot.send_message(chat_id,f"Ro‘yxatdan muvaffaqiyatli o‘tdingiz, {user_firstname[chat_id]} {user_lastname[chat_id]}!", reply_markup=get_student_menu(user_lang[chat_id]))
user_stage[chat_id]=None

# ============================================================

# ROLE SELECTION (teacher/student)

# ============================================================

@bot.message_handler(func=lambda m: m.text in ["O‘qituvchi 👨🏻‍🏫","Учитель 👨🏻‍🏫","O‘quvchi 🧑🏻‍🎓","Ученик 🧑🏻‍🎓"])
def choose_role(message):
chat_id = message.chat.id
lang = user_lang.get(chat_id)
if "O‘qituvchi" in message.text or "Учитель" in message.text:
user_role[chat_id]="teacher"
bot.send_message(chat_id,"Hozircha o‘qituvchilar uchun funksiyalar mavjud.", reply_markup=get_teacher_menu(lang))
else:
user_role[chat_id]="student"
bot.send_message(chat_id,"Quyidagilardan birini tanlang:", reply_markup=get_student_menu(lang))

# ============================================================

# STUDENT: FAN TESTLARI

# ============================================================

@bot.message_handler(func=lambda m: user_role.get(m.chat.id)=="student" and m.text in ["Fan testlari 🔖","Тесты по предметам 🔖"])
def test_menu(message):
chat_id = message.chat.id
lang = user_lang.get(chat_id)
bot.send_message(chat_id,"Qaysi test turini tanlaysiz?", reply_markup=get_test_types(lang))
user_stage[chat_id]="choose_test_type"

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="choose_test_type")
def test_type_handler(message):
chat_id = message.chat.id
lang = user_lang.get(chat_id)
if message.text=="↩️ Orqaga":
bot.send_message(chat_id,"Bosh menyu", reply_markup=get_student_menu(lang))
user_stage[chat_id]=None
return
user_stage[chat_id]="choose_test_level"
user_class[chat_id]=message.text
bot.send_message(chat_id,"Siz qaysi darajada test ishlamoqchisiz?", reply_markup=get_test_levels(lang))

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="choose_test_level")
def test_level_handler(message):
chat_id = message.chat.id
lang = user_lang.get(chat_id)
if message.text=="↩️ Orqaga":
bot.send_message(chat_id,"Qaysi test turini tanlaysiz?", reply_markup=get_test_types(lang))
user_stage[chat_id]="choose_test_type"
return
user_stage[chat_id]="choose_subject"
user_class[chat_id]=message.text
# Fanlarni chiqarish
sinf_int = int(user_class.get(chat_id,"5"))
if lang=="ru":
subjects = subjects_ru["<7"] if sinf_int<7 else subjects_ru[">=7"]
else:
subjects = subjects_uz["<7"] if sinf_int<7 else subjects_uz[">=7"]
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
for s in subjects:
markup.add(s)
markup.add("↩️ Orqaga")
bot.send_message(chat_id,"Ana endi qaysi fandan test ishlamoqchisiz?", reply_markup=markup)

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id)=="choose_subject")
def choose_subject_test(message):
chat_id = message.chat.id
lang = user_lang.get(chat_id)
if message.text=="↩️ Orqaga":
bot.send_message(chat_id,"Siz qaysi darajada test ishlamoqchisiz?", reply_markup=get_test_levels(lang))
user_stage[chat_id]="choose_test_level"
return
bot.send_message(chat_id,f"{message.text} fanidan testlar tez orada mavjud bo‘ladi ⏳!")

# ============================================================

# UNIVERSAL RESTART

# ============================================================

@bot.message_handler(commands=["restart"])
def universal_restart(message):
bot.reply_to(message,"Bot qayta ishga tushirilmoqda...")
threading.Thread(target=lambda: os._exit(0)).start()

# ============================================================

# BOT START

# ============================================================

if **name**=="**main**":
print("Bot ishga tushdi...")
try:
bot.infinity_polling(none_stop=True)
except:
import time
time.sleep(5)
os.execv(**file**,['python'] + [**file**])
