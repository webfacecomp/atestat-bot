import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN") 
print("TOKEN VALUE >>>", repr(TOKEN))
bot = telebot.TeleBot(TOKEN)

user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rus = types.KeyboardButton("Rus 🇷🇺")
    uzb = types.KeyboardButton("Uzb 🇺🇿")
    markup.add(rus, uzb)

    bot.send_message(
        message.chat.id,
        "Assalomu alaykum!\nSiz qaysi tilda suhbatlashishni hohlaysiz?",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text in ["Rus 🇷🇺", "Uzb 🇺🇿"])
def choose_lang(message):
      chat_id = message.chat.id
      if message.text == "Rus 🇷🇺":
        user_lang[chat_id] = "ru"
        bot.send_message(chat_id, "Вы выбрали русский язык. Отлично!")

        # Ruscha tugmalar
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        teacher = types.KeyboardButton("Учитель 👨‍🏫")
        student = types.KeyboardButton("Ученик 👨‍🎓")
        markup.add(teacher, student)

        bot.send_message(chat_id, "Вы учитель или ученик?", reply_markup=markup)

      else:
        user_lang[chat_id] = "uz"
        bot.send_message(chat_id, "Siz o‘zbek tilini tanladingiz. Ajoyib!")

        # O‘zbekcha tugmalar
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        teacher = types.KeyboardButton("O‘qituvchi 👨‍🏫")
        student = types.KeyboardButton("O‘quvchi 👨‍🎓")
        markup.add(teacher, student)

        bot.send_message(chat_id, "Siz o‘qituvchimisiz yoki o‘quvchi?", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text in [
    "Учитель 👨‍🏫", "Ученик 👨‍🎓",
    "O‘qituvchi 👨‍🏫", "O‘quvchi 👨‍🎓"
])
def role_chosen(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "uz")  # default uz agar topilmasa

    # Ruscha javob
    if lang == "ru":
        if message.text == "Учитель 👨‍🏫":
            bot.send_message(chat_id, "Отлично! Вы выбрали роль учителя.")
        else:
            bot.send_message(chat_id, "Хорошо! Вы выбрали роль ученика.")

    # O‘zbekcha javob
    else:
        if message.text == "O‘qituvchi 👨‍🏫":
            bot.send_message(chat_id, "Zo‘r! Siz o‘qituvchi rolini tanladingiz.")
        else:
            bot.send_message(chat_id, "Yaxshi! Siz o‘quvchi rolini tanladingiz.")


bot.infinity_polling()