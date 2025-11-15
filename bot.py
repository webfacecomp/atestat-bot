import os
import telebot
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom, ishga tushdim!")

@bot.message_handler(commands=['restart'])
def start(message):
    bot.reply_to(message, "Bot qayta yuklandi!")

bot.infinity_polling()