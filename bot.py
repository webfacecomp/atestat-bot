import telebot
import os

TOKEN = os.getenv("8514788206:AAGeVapTQe1oGcLt1io5J3zbc4885eh1dZM")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom, ishga tushdim!")

bot.infinity_polling()