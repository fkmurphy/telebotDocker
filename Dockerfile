FROM python:3.7-alpine

#Directorio de trabajo
WORKDIR /bot

# instalar git
RUN apk add git

# Obtener el repositorio de pyTelegramBotAPI

COPY ./pyTelegramBotAPI /bot/pyTelegramBotAPI 

# Instalar pyTelegramBotAPI
RUN cd /bot/pyTelegramBotAPI && \
     python setup.py install

ADD ./app /bot/app

ENV APIKEY INSERTAR-API-KEY

CMD ["python","./app/bot.py"]
