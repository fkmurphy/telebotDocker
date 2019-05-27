# Telegram BOT dockerized
Este contenedor basado en la imagen python3.7-apine utiliza la librería [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) para programar un BOT en Telegram. Es necesario generar un nuevo bot con [BotFather](https://telegram.me/BotFather) y obtener la API KEY.

Para programar el BOT, modifique el archivo **bot.py** en la carpeta _app_

## Para usar:

**Si se modifica Dockerfile cree la imagen de la siguiente manera:**

`$ docker build -t docker-telebot .`

**Crear un contendor**

`$ docker run --name telebot -e APIKEY="TUAPIKEY" -dit fkmurphy/python_telegram_bot`

