import os
import telebot
from telebot import types

TOKEN = os.getenv("8514788206:AAGeVapTQe1oGcLt1io5J3zbc4885eh1dZM")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rus = types.KeyboardButton("Rus 🇷🇺")
    uzb = types.KeyboardButton("Uzb 🇺🇿")
    markup.add(rus, uzb)

    bot.send_message(
        message.chat.id,
        "Assalomu alaykum!\nSiz qaysi tilda suhbatlashishni yoqtirasiz?",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text in ["Rus 🇷🇺", "Uzb 🇺🇿"])
def choose_lang(message):
    if message.text == "Rus 🇷🇺":
        bot.send_message(message.chat.id, "Вы выбрали русский язык. Отлично!")
    else:
        bot.send_message(message.chat.id, "Siz o‘zbek tilini tanladingiz. Ajoyib!")

bot.infinity_polling()
