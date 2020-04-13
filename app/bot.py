import telebot
from telebot import types
import logging
import requests

#import mong
from pymongo import MongoClient
from pprint import pprint

from html.parser import HTMLParser

import os
import sys
from time import sleep
#sys.path.insert(1,'./scripts/')
from scripts.getTemp import getStat
from scripts.proxmox import Proxmox 
from scripts.snmpservers import getSNMPStatus
from scripts.ultrasonido import dateRangeUltrasonic 
import library.environment.envs as env

ENV=env.read(".env")
#bot = telebot.TeleBot(ENV['TELEGRAM_BOT_API_KEY'])
#bot = None

URL = ENV['GLPI_URL']
appToken=ENV['GLPI_APP_TOKEN']
contentType=ENV['CONTENT_TYPE']
fileListIP=ENV['FILE_LIST_IP']
SESSION_SAVE="sessions/"

# parametros para conexion con telegram
BOT_TIMEOUT=3
BOT_INTERVAL=5

logging.basicConfig(filename='bitacora-bot.log',filemode='a',format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

client = MongoClient('192.168.42.19',27017)
db = client.test_database
if db:
    print("correcto")
else:
    print("noconecta")

def bot_polling():
    #global bot
    print("Comenzando")
    while True:
        try:
            # intentar conectar a telegram
            #bot = telebot.TeleBot
            bot = telebot.TeleBot(ENV['TELEGRAM_BOT_API_KEY'])
            botactions(bot)
            bot.polling(none_stop=True,interval=BOT_INTERVAL,timeout=BOT_TIMEOUT)
        except Exception as ex:
            bot.stop_polling()
            sleep(BOT_TIMEOUT)
        else:
            bot.stop_polling()
            break

def bot_polling():
    #global bot
    print("Comenzando")
    while True:
        try:
            # intentar conectar a telegram
            #bot = telebot.TeleBot
            bot = telebot.TeleBot(ENV['TELEGRAM_BOT_API_KEY'])
            botactions(bot)
            bot.polling(none_stop=True,interval=BOT_INTERVAL,timeout=BOT_TIMEOUT)
        except Exception as ex:
            bot.stop_polling()
            sleep(BOT_TIMEOUT)
        else:
            bot.stop_polling()
            break

# tomar r.status_code de return
# o tomar json. En caso de no existir json: except ValueError

def botactions(bot):
    # esta funcion agrega las cabeceras correspondientes para la API GLPI
    # y luego retorna la consulta correspondiente a la api
    # Method GET
    # concatURL es el path de la api
    # PARAMS los parámetros como por ejemplo el token de sesión
    def getGLPI(concatURL,PARAMS):
        try:
            PARAMS['app_token']=appToken
            PARAMS['Content-Type']=contentType
            r = requests.get(url=URL+concatURL,params=PARAMS)
            return r
        except requests.exceptions.Timeout:
            logging.warning("Problemas de respuesta en GLPI")
        except  Exception as e:
            logging.warning("Error: "+str(e))


    # El usuario puede iniciar sesión
    # mediante el nombre de usuario TELEGRAM y el token
    # user Usuario de Telegram
    # token User_Token para glpi
    def logIn(user,token):
        initSession="initSession"
        PARAMS = {
            "user_token":token
        }
        data = getGLPI(initSession,PARAMS)
        codigoReturn = data.status_code
        try:
            data = data.json()
        except ValueError:
            logging.warning("Error al iniciar sesion")
            
        if 'session_token' in data and data['session_token'] != "":
            sessionToken=data['session_token']
        else:
            sessionToken=None
        if not sessionToken is None :
            #guardar la sesion en el archivo con el nombre
            # de usuario de telegram
            # escribir y pisar si existe w, sino actualizar seria w+
            f = open(SESSION_SAVE+user,"w")
            f.write(sessionToken)
            f.close()
        else:
            logging.warning("Hubo un problema al obtener la sesión: "+str(data))
        return codigoReturn

    # obtener Token de archivo
    # username usuario de telegram
    def getToken(username):
        if os.path.isfile(SESSION_SAVE+username):
            try:
                with open(SESSION_SAVE+username,'r') as f:
                    token = f.read()
                    params = {
                        'session_token': token
                    }
                    checkToken = getGLPI("getFullSession",params)
                    if checkToken.status_code != 200:
                        token = None
                        f.close()
                        os.remove(username)
            except IOError:
                logging.warning("El archivo no fue posible de acceder. La ruta es: "+SESSION_SAVE+username)
        else:
            token = None
            logging.info("Intento de obtención de token por usuario: "+username+", no se tiene archivo")
        return token


    # obtener nombre de usuario de GLPI
    def getUserNameGLPI(token):
        params = {
            'session_token': token
        }
        username = getGLPI("getFullSession",params)
        if username.status_code == 200:
            username = username.json()['session']
            username = username['glpiname']
            logging.info("Se obtiene el usuario: "+username+" de GLPI")
        else:
            username = None
            logging.warning("no se obtuvo un usuario de GLPI para el token "+token)
        return username
    
    def opciones(message):
        try:
            cmd = message.text
            if cmd == "Mis Tickets":
                getTickets(message)
            elif cmd == "Stats":
                dcStats(message)
            elif cmd == "Cerrar Sesion":
                cerrarSession(message)
            elif cmd == "Sensor-Movimiento":
                sensorProximidad(message)
            
        except Exception as e:
            bot.send_message(message.chat.id,"Hubo un error al respoder")
            logging.warning("Problema en las opciones: "+str(e)+" ----------FIN-----------")

    # iniciar
    @bot.message_handler(commands=['start'])
    def init(message):
        bot.reply_to(message, "Estoy disponible... escribe para comenzar"+
                "\n"+"Recuerde, debe tener un nombre de usuario en telegram")


    @bot.message_handler(commands=['go'])
    def commands(message):
        if(message.from_user.is_bot):
            logging.warning("Un bot intento inciar con GO")
        else:
            try:
                cid = message.chat.id
                bot.send_message(cid,"Seleccione una opción")
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                markup.add('Stats','Mis Tickets','Cerrar Sesion','Sensor-Movimiento')
                bot.send_chat_action(cid,'typing')
                msg = bot.reply_to(message,'Seleccione una operación',reply_markup=markup)
                msg = bot.register_next_step_handler(msg,opciones)
            except Exception as e:
                logging.warning("Hubo un problema "+str(e))
                bot.send_message(message.chat.id,"Hubo un error con el comando GO")
    
    # Comenzar autenticación
    @bot.message_handler(commands=['user_token'])
    def authentication(message):
        bot.reply_to(message,"Iniciando sesión")
        token=message.text[12:]
        username=message.chat.username
        resultado=logIn(username,token)
        if resultado == 200:
            logging.info('Inicio sesión '+username)
            bot.send_message(message.chat.id,'Inició sesión correctamente')
        else:
            logging.warning('No pudo iniciar sesión con el usuario '+username)
            bot.send_message(message.chat.id,'No se pudo iniciar sesión')


    # Cerrar la sesión de un usuario
    @bot.message_handler(commands=['logout'])
    def cerrarSession(message):
        usuario=message.chat.username
        bot.reply_to(message,"Intentando cerrar sesión")
        token=getToken(usuario)

        if token != None:
            killSession = "killSession"
            PARAMS={
                'session_token':token
            }
            result = getGLPI(killSession,PARAMS)
            if result.status_code == 200: 
                if os.path.isfile(usuario):
                    os.remove(usuario)
                logging.info("Cerró la sesión "+usuario)
                bot.send_message(message.chat.id,'Se cerró la sesión con éxito');
            else:
                logging.warning("El usuario "+usuario+" no pudo cerrar la sesión")
                bot.send_message(message.chat.id,'Quizá ya cerró la sesión. No se ha podido realizar esta operación')
    
    
    #obtener incidentes de un usuario
    @bot.message_handler(commands=['ticket'])
    def getTickets(message):
        username=message.chat.username
        token=getToken(username)
        logging.info("El usuario "+username+" consulta los tickets")
         
        if token == None:
            logging.warning("Intento de consulta de tickets sin iniciar sesión "+username)
            bot.send_message(message.chat.id,"Inicie sesión")
            return

        #obtener nombre de usuario GLPI
        userGLPI = getUserNameGLPI(token)
        if userGLPI != None:  
            params = {
                'is_deleted':0,
                'criteria[0][link]':'AND',
                'criteria[0][field]':'12', # en proceso
                'criteria[0][searchtype]':'equals',
                'criteria[0][value]':'2',
                'criteria[1][link]':'AND',
                'criteria[1][field]':'5',#tecnico asgnado
                'criteria[1][searchtype]':'contains',
                'criteria[1][value]':userGLPI,
                'itemtype':'Ticket',
                'start':0,
                'session_token':token,
            }
            # obtener tickets
            tickets=getGLPI("search/Ticket/",params)
            # si hay tickets
            if tickets.status_code == 200:
                response=tickets.json()
                #procesarlos
                if 'data' in response and response['data']:
                    #print(response)
                    for ticket in response['data']:
                        idTicket=ticket['2']
                        # obtener info de ticket particular
                        ticketResponse = getGLPI('Ticket/'+str(idTicket),{
                            'session_token': token,
                        })
                        # si existe, formar string para enviar
                        if ticketResponse.status_code == 200 :
                            infoTicket=ticketResponse.json()
                            if 'id' in infoTicket:
                                title=infoTicket['name']
                                content=infoTicket['content']
                                apertura=infoTicket['date']
                                respuesta=("--------\n"+
                                "Titlulo:"+title+
                                "\nFecha de Apertura: "+apertura+
                                "\nContenido: "+content+
                                "\n-------------\n")
                                bot.send_message(message.chat.id,respuesta,parse_mode='HTML')
                else:
                    bot.send_message(message.chat.id,"No hay tickets para "+userGLPI)
            else:
                bot.send_message(message.chat.id,"Hubo un problema al obtener los tickets, error "+tickets.status_code)
                logging.warning("problema al obtener tickets de: "+userGLPI)
        else:
            logging.warning('Problema al conseguir el usuario de '+username)
            bot.send_message(message.chat.id, "Hubo un problema al"+
                "conseguir su usuario de GLPI")

    ## consultar humedad y temperatura
    @bot.message_handler(commands=['dcstats'])
    def dcStats(message):
        token = getToken(message.chat.username)
        logging.info("El usuario "+message.chat.username+" hace consultade stats")
        if token == None :
            logging.warning("Intento de consulta de stats sin iniciar sesion "+message.chat.username)
            bot.send_message(message.chat.id,"No tiene una sesión iniciada")
        else:
            bot.reply_to(message,"Aguarde unos instantes")
            array=getStat(3)
            cid=message.chat.id
            proxmox= Proxmox(ENV['PROXMOX_IP'],ENV['PROXMOX_PASSWORD'],ENV['PROXMOX_USER'])
            mensaje=("La temperatura es: "+
                array['temp']+"°\n"+
                "La humedad es de: "+array['hum']+'%')
            # nodos proxmox
            mensaje+="\n<b>Nodos proxmox</b>\n"
            nodos = proxmox.getNodeStat()
            for nodo in nodos:
                mensaje+=("{0} => {1}".format(nodo['node'],nodo['status']))
                mensaje+="\n"
            ## mauqinas y contenedores proxmox
            proxmoxVM=proxmox.getVMStat()
            mensaje+="<b>VMs Proxmox:</b> \n"
            #estructura de getVMStat
            # array {vmid: id, name:string, status: string}
            for vm in proxmoxVM:
                mensaje+=("{0}. {1} => {2}" .format(vm['vmid'],vm['name'],vm['status'])+"\n")
    
            #servidores 
            mensaje+="<b>Servidores</b>\n"
            servers=getSNMPStatus(fileListIP)
            for server in servers:
                mensaje+=("{0} => {1}".format(str(server),servers[str(server)])+"\n")
            bot.send_message(cid,mensaje,parse_mode='HTML')

    @bot.message_handler(commands=['sens'])
    def sensorProximidad(message):
        token = getToken(message.chat.username)
        logging.info("El usuario "+message.chat.username+" hace consultade stats")
        if token == None :
            logging.warning("Intento de consulta de stats sin iniciar sesion "+message.chat.username)
            bot.send_message(message.chat.id,"No tiene una sesión iniciada")
        else:
            info = dateRangeUltrasonic()
            if len(info) > 20:
                info = dict(list(info.items())[len(info)-20:])
            listIncidentes="<b>Ultimos 20 movimientos detectados en los ultimos 2 días</b>\n"
            for incidente in info:
                listIncidentes+=info[incidente]+"\n"
            bot.send_message(message.chat.id,listIncidentes,parse_mode='HTML')


#bot.polling()
bot_polling()
