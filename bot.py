import telebot
import os
import platform

bot = telebot.TeleBot(os.environ.get('APIKEY'))

def informacion():
    message="Arquitectura"+platform.architecture()[0]+"\nMaquina "+platform.machine()+"\n"
    with open("/proc/meminfo","r") as f:
        lines = f.readlines()
    message+="   "+lines[0].strip()+" \n"
    message+="   "+lines[1].strip()
    return message;
            
@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.reply_to(message, informacion())

bot.polling()
