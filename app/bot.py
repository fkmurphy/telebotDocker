#!/usr/bin/python
#-*- coding:utf-8 -*-
import telebot
from telebot import types
import os #os.system(comando) y environment
#ejecutar comandos con sub.Popen(['comando','arg'],stdout=sub.PIPE,stderr=sub.PIPE)
# output,errors = p.communicate()
import subprocess as sub 
# para informacion del sistema import platform

#peticiones
import requests
#descargas
from datetime import datetime

print ("[System] Bot has started.")

bt = telebot.TeleBot("710493136:AAHoHtPJ8ohWEwrUPUjzHLi-U2fdT5swkjQ")
cmdUserDictionary = {}



def parametros(m):
    array = m.split()
    del array[0]
    return array;

class Server:
    def __init__(self, ip):
        self.ip = ip
        

class Sender:
    def __init__(self, ip):
        self.ip = ip
        self.cmd = ""
        self.args = ""
    def setCMD(cmd):
        self.cmd = cmd

def getCommand(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None



@bt.message_handler(commands=['help'])
def help(m):
    try:
        cid = m.chat.id
        bt.send_message(cid,"Comience a utilizar el bot con /go")
    except Exception as e:
        bt.repply_to(m,"Error Help")

@bt.message_handler(commands=['go'])
def command(message):
    # si es un bot el que me habla entonces lo despido
    if ( message.from_user.is_bot ):
        print("Ey, trató un bot")
        bt.reply_to(message,"Bye!")
    else:        
        welcome = "Bienvenido! este es un bot para administrar servidores."
        try:
            if message.chat.username == None:
                msg = bt.reply_to(message,'Debe asignarse un nombre de usuario en Telegram')
            else:
                cid = message.chat.id
                bt.send_message(cid,"Seleccione una opción")
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                markup.add('Comando','Lista de servidores')
                bt.send_chat_action(cid,'typing')
                msg = bt.reply_to(message, ' Seleccione una operación', reply_markup=markup)
                msg = bt.register_next_step_handler(msg,opciones)
            
        except Exception as e:
            bt.reply_to(message,"ERROR en comienzo")

def opciones(message):
    try:
        cmd = message.text
        if cmd == 'Lista de servidores':
            getList(message)
        elif cmd == 'Comando':
            comando(message)
        else:
            print("ERROR NO ES NINGUN COMANDO")
            bt.reply_to(message, 'no hay un comando')
    except Exception as e:
        bt.reply_to(message, 'error en opciones')

def comando(m):
    try:
        cid = m.chat.id
        # elegir servidor
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        lista = serverListProp("nombre")
        markup.add(*lista)
        msg = bt.reply_to(m, 'Elija un servidor', reply_markup=markup)
        msg = bt.register_next_step_handler(m,derivar,"")
    except Exception as e:
        bt.reply_to(message, 'Error en comando')


def serverListProp(search):
    lista = requests.get('http://admin.django.curza/servidores/')
    string="Servidores:\n"
    array = []
    for srv in lista.json():
        array.append(srv[search])
    return array
def serverListKV(key,value):
    lista = requests.get('http://admin.django.curza/servidores/')
    string="Servidores:\n"
    array = {}
    for srv in lista.json():
        array[srv[key]] = srv[value]
    return array


def derivar(m,status):
    try:
        #if not cmdUserDictionary[m.username]:
        #creo un sender con ip m.text
        if not (m.chat.username in cmdUserDictionary):
            lista = serverListKV("nombre","ip")
            sender = Sender(lista[m.text])
            cmdUserDictionary[m.chat.username] = sender
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('scp', 'ls', 'cat','discos')
            msg = bt.reply_to(m, ' Seleccione una operación', reply_markup=markup)
            msg = bt.register_next_step_handler(msg,derivar,"waitCMD")
        else:
            send = cmdUserDictionary[m.chat.username]
            if status == "waitCMD":
                if m.text == "discos" :
                    send.cmd = "df"
                    msg = bt.reply_to(m,"Ingrese argumentos para el comando DF")
                else:    
                    send.cmd = m.text
                    sendMSG = "Ingrese argumentos del comando"
                    if send.cmd == "cat":
                        sendMSG = "Ingrese el archivo para CAT (PWD: /home/"+m.chat.username+"/"
                    elif send.cmd == "scp":
                        sendMSG = "Ingrese el directorio absoluto a obtener"
                    elif send.cmd == "ls":
                        sendMSG = "Ingrese argumentos de formato para LS o un punto para obtener el directorio actual /home/"+m.chat.username+"/"
                    msg = bt.reply_to(m,sendMSG)
                msg = bt.register_next_step_handler(m,derivar,"waitARG")
            
            if status == "waitARG":
                send.args = m.text
                status = "finish"
            
            if status == "finish":
                r = requests.post('http://admin.django.curza/servidores/',
                        data={
                            "cmd":send.cmd,
                            "server":send.ip,
                            "args":send.args,
                            "username": m.chat.username
                        })
                print(r.json())
                cid = m.chat.id
                json=r.json()

                # si la respuesta es una url de archvio:
                if ('urlFile' in json and json['urlFile'] != "" ):
                    file_name = json['urlFile'].split('/')[-1]
                    today = datetime.now().strftime("%d%m%Y_%H%M%S")
                    url = "http://admin.django.curza"+json['urlFile']
                    args = "-P /bot/media/"
                        #cmd = sub.Popen(['wget',url, '> media/'],stdout=sub.PIPE,stderr=sub.PIPE)
                        #cmd.wait()
                        #cmd.communicate()
                    if os.path.splitext(file_name)[-1].lower() == '.zip':
                        os.system("cd /bot/media/ && wget "+url+" -O"+file_name)
                        bt.send_message(cid,'El archivo '+file_name+' se está enviando')
                        bt.send_document(cid, open('/bot/media/'+file_name, 'rb'))          
                    else:
                        os.system("cd /bot/media/ && wget "+url+" -O"+file_name+today)
                        bt.send_message(cid,'El archivo '+file_name+today+' se está enviando')
                        bt.send_document(cid, open('/bot/media/'+file_name+today, 'rb'))          
                
                else:
                    #si la respuesta no es una url de archivo
                    #mensaje = parseJson(r.json())
                    if "Error" in json:
                        bt.send_message(cid,"Hubo un error: "+json['Error'])
                    else:
                        bt.send_message(cid,json['mensaje'])
                if (m.chat.username in cmdUserDictionary):
                    del cmdUserDictionary[m.chat.username]

    except Exception as e:
        if (m.chat.username in cmdUserDictionary):
            del cmdUserDictionary[m.chat.username]
        bt.reply_to(m, 'Error en comando')

def parseJson(json):
    string ="Respuesta "
    for msgReturn in json['mensaje']:
        string += msgReturn
    return string

def getList(m):
    lista = requests.get('http://admin.django.curza/servidores/')
    string="Servidores:\n"

    for srv in lista.json():
        string = string +"Hostname: "+srv['nombre']+"\n\t\t\tIPv4: "+srv['ip']+"\n\n"
        #msg = requests.get('http://admin.django.curza/usuarios/1/')
           
    bt.send_message(m.chat.id,string)

def executeLS(message):
    bt.reply_to(message,"ejecuto ls")

def error(message):
    print("hubo un error")


bt.enable_save_next_step_handlers(delay=2)
bt.load_next_step_handlers()
bt.polling()
