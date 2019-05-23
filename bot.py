import telebot
import os

bot = telebot.TeleBot(os.environ.get('APIKEY'))
@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.reply_to(message, "Hola  Mundo")

bot.polling()
