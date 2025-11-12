import telebot

bot = telebot.TeleBot('8514788206:AAGeVapTQe1oGcLt1io5J3zbc4885eh1dZM')

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, 'Assalomu alaykum!')

@bot.message_handler(commands=['restart'])
def main(message):
    bot.send_message(message.chat.id, 'Bot qayta yuklandi')


bot.polling()
