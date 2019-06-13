FROM python:3.7-alpine

#Directorio de trabajo
WORKDIR /bot

# instalar git
RUN apk add git

# Obtener el repositorio de pyTelegramBotAPI

COPY ./pyTelegramBotAPI /bot/pyTelegramBotAPI 
COPY ./Pipfile /bot/

# Instalar pyTelegramBotAPI
RUN cd /bot/pyTelegramBotAPI && \
     python setup.py install && \
     pip install pipenv && \
     pipenv lock && \
     pipenv install --system

ADD ./app /bot/app

ENV APIKEY INSERTAR-API-KEY

ENV PYTHONUNBUFFERED 1
CMD ["python","./app/bot.py"]
