FROM python:3.7-alpine

#Directorio de trabajo
WORKDIR /bot

# instalar git
RUN apk add git

# Obtener el repositorio de pyTelegramBotAPI
RUN git clone https://github.com/eternnoir/pyTelegramBotAPI.git

# Iniciar bot
COPY ./bot.py /bot/bot.py

# Instalar pyTelegramBotAPI
RUN cd /bot/pyTelegramBotAPI && \
     python setup.py install

#ADD ./app /bot/app
# correr el script
COPY ./entrypoint.sh /bot/entrypoint.sh 
ENTRYPOINT ["/bot/entrypoint.sh"]

CMD ["python","bot.py"]
