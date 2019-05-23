# Telegram BOT dockerized

Este es un contenedor para crear un bot bajo el proyecto [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)

## Para probar:

**Crear la imagen**
`$ docker build -t telebot .`

**Crear un contendor**
`$ docker run -dit dockertelebot`
**o sino,**
`$ docker run -dit --rm -v $PWD/bot.py:/bot/bot.py telebot`
