import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = "YOUR_TOKEN_HERE"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# =====================
# FOYDALANUVCHI HOLATLARI (FSM)
# =====================

class UserState(StatesGroup):
    waiting_for_language = State()
    waiting_for_contact = State()
    waiting_for_name = State()
    waiting_for_role = State()

    # Student menu
    student_menu = State()
    student_test_category = State()
    student_test_grade = State()
    student_test_subject = State()

# =====================
# KLAVIATURALAR
# =====================

def language_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English")
    return kb

def contact_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📱 Share contact", request_contact=True))
    return kb

def back_button():
    return ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️ Orqaga")

def role_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("👨‍🏫 O‘qituvchi", "🧑‍🎓 O‘quvchi")
    return kb

def student_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📚 Dars jadvali")
    kb.add("📝 Fan testlari")
    kb.add("⬅️ Orqaga")
    return kb

def test_category_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🔥 Qiziquvchilar uchun testlar")
    kb.add("🏆 Olimpiada testlar")
    kb.add("⬅️ Orqaga")
    return kb

def grade_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("5", "6", "7")
    kb.row("8", "9", "10", "11")
    kb.add("⬅️ Orqaga")
    return kb

# Fanlar (dinamik hosil qilinadi)
def get_subjects_by_grade(grade):
    subjects = []

    if int(grade) <= 6:
        subjects = ["Matematika", "Ingliz tili", "Rus tili", "Ona tili",
                    "Tarix", "Adabiyot", "Geografiya", "Biologiya"]
    else:
        subjects = ["Algebra", "Geometriya", "Ingliz tili", "Rus tili",
                    "Ona tili", "O‘zbekiston tarixi", "Jahon tarixi",
                    "Fizika", "Adabiyot", "Geografiya", "Biologiya"]

    return subjects

def subject_keyboard(grade):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for s in get_subjects_by_grade(grade):
        kb.add(s)
    kb.add("📌 Menga kerakli fan yo‘q")
    kb.add("⬅️ Orqaga")
    return kb

# =====================
# START COMMAND
# =====================

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Tilni tanlang:", reply_markup=language_keyboard())
    await UserState.waiting_for_language.set()

# =====================
# 1. TIL TANLASH
# =====================

@dp.message_handler(state=UserState.waiting_for_language)
async def choose_language(message: types.Message, state: FSMContext):
    await message.answer("Iltimos, kontaktingizni yuboring:", reply_markup=contact_keyboard())
    await UserState.waiting_for_contact.set()

# =====================
# 2. SHARE CONTACT — LOGIN / RO‘YXATDAN O‘TISH
# =====================

@dp.message_handler(content_types=['contact'], state=UserState.waiting_for_contact)
async def get_contact(message: types.Message, state: FSMContext):

    # bu yerda user bazaga yoziladi (backend yo‘q — shunchaki saqlab turamiz)
    await state.update_data(phone=message.contact.phone_number,
                            user_id=message.from_user.id)

    await message.answer("Ism va familyangizni kiriting:", reply_markup=back_button())
    await UserState.waiting_for_name.set()

# =====================
# 3. FOYDALANUVCHI ISMI
# =====================

@dp.message_handler(state=UserState.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await start_cmd(message)
        return

    await state.update_data(full_name=message.text)
    await message.answer("Endi rolingizni tanlang:", reply_markup=role_keyboard())
    await UserState.waiting_for_role.set()

# =====================
# 4. ROLE TANLASH
# =====================

@dp.message_handler(state=UserState.waiting_for_role)
async def choose_role(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await message.answer("Tilni tanlang:", reply_markup=language_keyboard())
        await UserState.waiting_for_language.set()
        return

    if message.text == "🧑‍🎓 O‘quvchi":
        await message.answer("O‘quvchi menyusi:", reply_markup=student_menu_keyboard())
        await UserState.student_menu.set()
        return

    if message.text == "👨‍🏫 O‘qituvchi":
        await message.answer("O‘qituvchilar bo‘limi hali sinab ko‘rilmoqda 😊")
        return

    await message.answer("Iltimos, pastdagi tugmalardan birini tanlang.")



# =====================
# 5. O‘QUVCHI MENYUSI
# =====================

@dp.message_handler(state=UserState.student_menu)
async def student_menu_handler(message: types.Message, state: FSMContext):
    text = message.text

    # orqaga
    if text == "⬅️ Orqaga":
        await message.answer("Endi rolingizni tanlang:", reply_markup=role_keyboard())
        await UserState.waiting_for_role.set()
        return

    # Dars jadvali (eski funksiya — unga tegmadim)
    if text == "📚 Dars jadvali":
        await message.answer("Dars jadvali funksiyasi mavjud 📘")
        return

    # Testlar bo‘limiga kirish
    if text == "📝 Fan testlari":
        await message.answer("Qaysi turdagi testlarni ishlamoqchisiz?", 
                             reply_markup=test_category_keyboard())
        await UserState.student_test_category.set()
        return

    await message.answer("Menyudan tugmani tanlang.")



# =====================
# 6. TEST KATEGORIYASI TANLANADI
# =====================

@dp.message_handler(state=UserState.student_test_category)
async def test_category_handler(message: types.Message, state: FSMContext):
    text = message.text

    if text == "⬅️ Orqaga":
        await message.answer("O‘quvchi menyusi:", reply_markup=student_menu_keyboard())
        await UserState.student_menu.set()
        return

    if text not in ["🔥 Qiziquvchilar uchun testlar", "🏆 Olimpiada testlar"]:
        await message.answer("Quyidagi menyudan birini tanlang.")
        return

    # test turini saqlaymiz
    await state.update_data(test_type=text)

    await message.answer("Endi sinfni tanlang:", reply_markup=grade_keyboard())
    await UserState.student_test_grade.set()



# =====================
# 7. SINF TANLANADI
# =====================

@dp.message_handler(state=UserState.student_test_grade)
async def grade_handler(message: types.Message, state: FSMContext):
    grade = message.text

    if grade == "⬅️ Orqaga":
        await message.answer("Qaysi turdagi testlarni ishlamoqchisiz?",
                             reply_markup=test_category_keyboard())
        await UserState.student_test_category.set()
        return

    if grade not in ["5","6","7","8","9","10","11"]:
        await message.answer("Iltimos, sinfni tanlang.")
        return

    await state.update_data(grade=grade)

    await message.answer(f"{grade}-sinf testlari. Endi fanni tanlang:",
                         reply_markup=subject_keyboard(grade))
    await UserState.student_test_subject.set()



# =====================
# 8. FAN TANLANADI
# =====================

@dp.message_handler(state=UserState.student_test_subject)
async def subject_handler(message: types.Message, state: FSMContext):
    subject = message.text
    data = await state.get_data()
    grade = data['grade']

    if subject == "⬅️ Orqaga":
        await message.answer("Endi sinfni tanlang:", reply_markup=grade_keyboard())
        await UserState.student_test_grade.set()
        return

    if subject == "📌 Menga kerakli fan yo‘q":
        await message.answer(
            "Sizga kerakli fan bu ro‘yxatda bo‘lmasa u tez kunlarda qo‘shiladi ⏳!"
        )
        return

    # fan ro‘yxatda borligini tekshiramiz
    valid_subjects = get_subjects_by_grade(grade)

    if subject not in valid_subjects:
        await message.answer("Tanlov noto‘g‘ri. Quyidagi fanlardan birini tanlang:",
                             reply_markup=subject_keyboard(grade))
        return

    # Agar fan tanlansa, test boshlanadi (hozircha testlar yo‘q — placeholder)
    await message.answer(f"{subject} bo‘yicha testlar tez orada qo‘shiladi 📘")

    # O‘quvchi menyusiga qaytaramiz
    await message.answer("O‘quvchi menyusi:", reply_markup=student_menu_keyboard())
    await UserState.student_menu.set()

# ============================================================
# 3-QISM — O‘QITUVCHILAR PANELI (YILLIK DARS REJASI)
# ============================================================

# Guruhlar ro‘yxati
teacher_groups = {
    "5": ["5-01", "5-02", "5-03"],
    "6": ["6-01", "6-02", "6-03"],
    "7": ["7-01", "7-02", "7-03"],
    "8": ["8-01", "8-02", "8-03"],
    "9": ["9-01", "9-02", "9-03"],
    "10": ["10-01", "10-02"],
    "11": ["11-01", "11-02"]
}

# HOLATLAR
class TeacherState(StatesGroup):
    menu = State()
    choose_class = State()
    choose_group = State()
    choose_subject = State()


# O‘QITUVCHI MENYUSI
@dp.message_handler(lambda msg: msg.text in ["👨‍🏫 O‘qituvchi", "👩‍🏫 Учитель"], state="*")
async def teacher_menu(message: types.Message, state: FSMContext):
    await state.finish()

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📘 Sinflar uchun yillik dars rejasi")
    kb.add("⬅️ Orqaga")

    await message.answer("O‘qituvchi bo‘limiga xush kelibsiz!", reply_markup=kb)
    await TeacherState.menu.set()


# M E N Y U → S I N F   T A N L A S H
@dp.message_handler(state=TeacherState.menu)
async def teacher_menu_handler(message: types.Message, state: FSMContext):
    text = message.text

    if text == "⬅️ Orqaga":
        await message.answer("Rolingizni tanlang:", reply_markup=role_keyboard())
        await UserState.waiting_for_role.set()
        return

    if text == "📘 Sinflar uchun yillik dars rejasi":
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(5, 12):
            kb.add(f"{i}-sinf")
        kb.add("⬅️ Orqaga")

        await message.answer("Qaysi sinfning rejasini ko‘rmoqchisiz?", reply_markup=kb)
        await TeacherState.choose_class.set()


# S I N F   T A N L A N G A C H   →   G U R U H
@dp.message_handler(state=TeacherState.choose_class)
async def teacher_choose_class(message: types.Message, state: FSMContext):
    text = message.text.replace("-sinf", "")

    if message.text == "⬅️ Orqaga":
        await teacher_menu(message, state)
        return

    if text not in teacher_groups:
        await message.answer("Iltimos, ro‘yxatdan sinfni tanlang.")
        return

    await state.update_data(teacher_class=text)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for g in teacher_groups[text]:
        kb.add(g)
    kb.add("⬅️ Orqaga")

    await message.answer("Qaysi guruh?", reply_markup=kb)
    await TeacherState.choose_group.set()


# G U R U H   T A N L A N G A C H   →   F A N
@dp.message_handler(state=TeacherState.choose_group)
async def teacher_choose_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sinf = data["teacher_class"]

    if message.text == "⬅️ Orqaga":
        await teacher_menu_handler(message, state)
        return

    if message.text not in teacher_groups[sinf]:
        await message.answer("Ro‘yxatdan guruhni tanlang.")
        return

    await state.update_data(teacher_group=message.text)

    # FANLAR
    subjects = []
    if int(sinf) < 7:
        subjects = [
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
        subjects = [
            "Algebra", "Geometriya",
            "Inglis tili",
            "Rus tili",
            "Ona tili",
            "O‘zbekiston tarixi", "Jahon tarixi",
            "Adabiyot",
            "Geografiya",
            "Biologiya",
            "Fizika"
        ]

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for s in subjects:
        kb.add(s)
    kb.add("📌 Menga kerakli fan yo‘q")
    kb.add("⬅️ Orqaga")

    await message.answer("Qaysi fan bo‘yicha reja kerak?", reply_markup=kb)
    await TeacherState.choose_subject.set()


# F A N   T A N L A N G A C H   →   N A T I J A
@dp.message_handler(state=TeacherState.choose_subject)
async def teacher_choose_subject(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sinf = data["teacher_class"]
    group = data["teacher_group"]
    subject = message.text

    if subject == "⬅️ Orqaga":
        await teacher_choose_class(message, state)
        return

    if subject == "📌 Menga kerakli fan yo‘q":
        await message.answer("Bu fan tez orada qo‘shiladi ⏳!")
        return

    await message.answer(
        f"{sinf}-sinf {group} uchun *{subject}* bo‘yicha yillik reja tez orada qo‘shiladi ⏳!",
        parse_mode="Markdown"
    )

    # Yakun
    await message.answer("O‘qituvchi menyusi:", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
        "📘 Sinflar uchun yillik dars rejasi", "⬅️ Orqaga"
    ))
    await TeacherState.menu.set()

# ============================================================
# 4-QISM — STUDENT (DARS JADVALI FUNKSIYASI KUCHAYTIRILGAN)
# ============================================================

class ScheduleState(StatesGroup):
    choose_class = State()
    choose_group = State()


# 📑 Dars jadvali tugmasi bosilganda
@dp.message_handler(lambda msg: msg.text in ["Dars jadvali 📑", "📑 Расписание уроков"], state="*")
async def schedule_start(message: types.Message, state: FSMContext):
    await state.finish()

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(5, 12):
        kb.add(f"{i}-sinf")
    kb.add("⬅️ Orqaga")

    await message.answer("Nechinchi sinf?", reply_markup=kb)
    await ScheduleState.choose_class.set()


# 🧩 SINFDAN SO‘NG – GURUH
@dp.message_handler(state=ScheduleState.choose_class)
async def schedule_choose_class(message: types.Message, state: FSMContext):
    text = message.text.replace("-sinf", "")

    if message.text == "⬅️ Orqaga":
        await message.answer("Asosiy menyu:", reply_markup=student_main_keyboard())
        return

    if text not in groups:
        await message.answer("Iltimos, ro‘yxatdan tanlang.")
        return

    await state.update_data(sinf=text)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for g in groups[text]:
        kb.add(g)
    kb.add("⬅️ Orqaga")

    await message.answer("Qaysi guruh?", reply_markup=kb)
    await ScheduleState.choose_group.set()


# 📸 GURUH TANLANGANDA → SURATNI YUBORISH
@dp.message_handler(state=ScheduleState.choose_group)
async def schedule_send(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sinf = data["sinf"]
    guruh = message.text

    if guruh == "⬅️ Orqaga":
        await schedule_start(message, state)
        return

    if guruh not in groups[sinf]:
        await message.answer("Ro‘yxatdan guruhni tanlang.")
        return

    # RASM YO‘L
    file_path = f"images/{guruh}.jpg"

    if not os.path.exists(file_path):
        await message.answer("Bu guruh uchun dars jadvali hali yuklanmagan ❗")
    else:
        with open(file_path, "rb") as img:
            await message.answer_photo(
                img,
                caption=f"{guruh} uchun dars jadvali 📘"
            )

    kb = student_main_keyboard()
    await message.answer("Yana qanday yordam kerak?", reply_markup=kb)
    await state.finish()

# ============================================================
# USER AUTH STORAGE
# ============================================================

user_phone = {}      # chat_id: phone_number
user_name = {}       # chat_id: full_name
user_registered = {} # chat_id: True/False

def auth_menu(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if lang == "uz":
        kb.add("📲 Login", "📝 Ro‘yxatdan o‘tish")
    else:
        kb.add("📲 Логин", "📝 Регистрация")
    return kb

bot.send_message(
    chat_id,
    "Davom etish uchun iltimos, ro‘yxatdan o‘ting yoki tizimga kiring:",
    reply_markup=auth_menu(lang)
)

@bot.message_handler(func=lambda m: m.text in ["📲 Login", "📲 Логин"])
def login_start(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(
        "📱 Contact yuborish" if lang == "uz" else "📱 Отправить контакт",
        request_contact=True
    )
    kb.add(button)

    bot.send_message(
        chat_id,
        "Davom etish uchun telefon raqamingizni yuboring:" if lang == "uz" else "Отправьте ваш номер телефона:",
        reply_markup=kb
    )

@bot.message_handler(func=lambda m: m.text in ["📝 Ro‘yxatdan o‘tish", "📝 Регистрация"])
def register_start(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(
        "📱 Contact yuborish" if lang == "uz" else "📱 Отправить контакт",
        request_contact=True
    )
    kb.add(button)

    bot.send_message(
        chat_id,
        "Ro‘yxatdan o‘tish uchun kontaktingizni yuboring:" if lang == "uz" else "Для регистрации отправьте контакт:",
        reply_markup=kb
    )

    user_stage[chat_id] = "register_contact"

@bot.message_handler(content_types=['contact'])
def contact_received(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    phone = message.contact.phone_number
    user_phone[chat_id] = phone

    if user_stage.get(chat_id) == "register_contact":
        bot.send_message(chat_id, "Ism familyangizni kiriting:", reply_markup=types.ReplyKeyboardRemove())
        user_stage[chat_id] = "register_name"
        return
    
    # LOGIN bo‘lsa
    user_registered[chat_id] = True
    bot.send_message(chat_id, "Tizimga muvaffaqiyatli kirdingiz!" if lang == "uz" else "Вы вошли в систему!")
    ask_role_after_auth(message)

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "register_name")
def register_name_finish(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    fullname = message.text.strip()
    user_name[chat_id] = fullname
    user_registered[chat_id] = True

    bot.send_message(chat_id, f"Ro‘yxatdan o‘tish yakunlandi, {fullname}!", reply_markup=types.ReplyKeyboardRemove())

    user_stage.pop(chat_id, None)
    ask_role_after_auth(message)

def ask_role_after_auth(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    if lang == "ru":
        markup.add("Информация о школе")
        markup.add("Ученик 🧑🏻‍🎓")
        markup.add("Учитель 👨🏻‍🏫")
    else:
        markup.add("Maktab haqida ma'lumot")
        markup.add("O‘quvchi 🧑🏻‍🎓")
        markup.add("O‘qituvchi 👨🏻‍🏫")

    bot.send_message(
        chat_id,
        "Davom etish uchun o‘z rolingizni tanlang:" if lang == "uz" else "Выберите вашу роль:",
        reply_markup=markup
    )

# ============================================================
# STUDENT → FAN TESTLARI — BOSHLANG‘ICH MENYU
# ============================================================

@bot.message_handler(func=lambda m: user_role.get(m.chat.id) == "student" and 
                     m.text in ["Fan testlari 🔖", "Тесты по предметам 🔖"])
def tests_main_menu(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    user_stage[chat_id] = "test_main"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    if lang == "ru":
        kb.add("Тесты для интересующихся 🔥")
        kb.add("Олимпиадные тесты 🏆")
        kb.add("◀️ Назад")
        kb.add("🏠 Главное меню")
    else:
        kb.add("Qiziquvchilar uchun testlar 🔥")
        kb.add("Olimpiada testlar 🏆")
        kb.add("◀️ Orqaga")
        kb.add("🏠 Bosh menyu")

    bot.send_message(chat_id,
                     "Qaysi turdagi testlarni ishlamoqchisiz?" if lang == "uz"
                     else "Выберите тип тестов:",
                     reply_markup=kb)

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "test_main")
def test_choose_grade(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")

    text = message.text

    # BACK
    if text in ["◀️ Orqaga", "◀️ Назад"]:
        bot.send_message(chat_id, 
                         "Quyidagilardan birini tanlang:" if lang == "uz"
                         else "Выберите один вариант:",
                         reply_markup=get_student_menu(lang))
        user_stage.pop(chat_id, None)
        return

    # HOME
    if text in ["🏠 Bosh menyu", "🏠 Главное меню"]:
        bot.send_message(chat_id, 
                         "Menyuga qaytdik." if lang == "uz" else "Возврат в меню.",
                         reply_markup=get_student_menu(lang))
        user_stage.pop(chat_id, None)
        return

    if text not in ["Qiziquvchilar uchun testlar 🔥", "Тесты для интересующихся 🔥",
                    "Olimpiada testlar 🏆", "Олимпиадные тесты 🏆"]:
        return

    user_stage[chat_id] = "test_grade_select"
    user_stage[f"{chat_id}_test_type"] = text

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    for i in range(5, 12):
        kb.add(f"{i}-sinf")

    kb.add("◀️ Orqaga" if lang == "uz" else "◀️ Назад")
    kb.add("🏠 Bosh menyu" if lang == "uz" else "🏠 Главное меню")

    bot.send_message(chat_id,
                     "Sinf darajasini tanlang:" if lang == "uz" 
                     else "Выберите класс:",
                     reply_markup=kb)

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "test_grade_select")
def test_choose_subject(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = message.text

    # BACK
    if text in ["◀️ Orqaga", "◀️ Назад"]:
        return tests_main_menu(message)

    # HOME
    if text in ["🏠 Bosh menyu", "🏠 Главное меню"]:
        bot.send_message(chat_id, 
                         "Menyuga qaytdik." if lang == "uz" else "Возврат в меню.",
                         reply_markup=get_student_menu(lang))
        user_stage.pop(chat_id, None)
        return

    if not text.endswith("-sinf"):
        return

    grade = int(text.replace("-sinf", ""))
    user_stage[f"{chat_id}_grade"] = grade

    subjects = subjects_uz["<7"] if lang == "uz" and grade < 7 else \
               subjects_ru["<7"] if lang == "ru" and grade < 7 else \
               subjects_uz[">=7"] if lang == "uz" else \
               subjects_ru[">=7"]

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    for s in subjects:
        kb.add(s)

    kb.add("Menga kerakli fan yo‘q ❗" if lang == "uz" else "Нужного предмета нет ❗")
    kb.add("◀️ Orqaga" if lang == "uz" else "◀️ Назад")
    kb.add("🏠 Bosh menyu" if lang == "uz" else "🏠 Главное меню")

    user_stage[chat_id] = "test_subject"

    bot.send_message(chat_id,
                     "Qaysi fandan test ishlamoqchisiz?" if lang == "uz"
                     else "Выберите предмет:",
                     reply_markup=kb)

@bot.message_handler(func=lambda m: user_stage.get(m.chat.id) == "test_subject")
def test_subject_result(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")
    text = message.text

    # BACK
    if text in ["◀️ Orqaga", "◀️ Назад"]:
        return test_choose_grade(message)

    # HOME
    if text in ["🏠 Bosh menyu", "🏠 Главное меню"]:
        bot.send_message(chat_id,
                         "Menyuga qaytdik." if lang == "uz" else "Возврат в меню.",
                         reply_markup=get_student_menu(lang))
        user_stage.pop(chat_id, None)
        return

    if text in ["Menga kerakli fan yo‘q ❗", "Нужного предмета нет ❗"]:
        bot.send_message(chat_id,
                         "Sizga kerakli fan bu ro‘yhatda bo‘lmasa u tez kunlarda qo‘shiladi ⏳!"
                         if lang == "uz" else
                         "Если нужного предмета нет — он будет добавлен позже ⏳!")
        return

    grade = user_stage.get(f"{chat_id}_grade")
    test_type = user_stage.get(f"{chat_id}_test_type")

    bot.send_message(
        chat_id,
        f"🔜 {grade}-sinf uchun *{text}* fanidan '{test_type}' testlari tez orada qo‘shiladi ⏳!" if lang == "uz" else
        f"🔜 Тесты по предмету *{text}* для {grade}-класса скоро появятся ⏳!",
        parse_mode="Markdown"
    )

    # cleanup
    user_stage.pop(chat_id, None)
    user_stage.pop(f"{chat_id}_grade", None)
    user_stage.pop(f"{chat_id}_test_type", None)

    bot.send_message(chat_id,
                     "Yana bo‘lim tanlang:" if lang == "uz"
                     else "Выберите следующий раздел:",
                     reply_markup=get_student_menu(lang))

bot.infinity_polling()