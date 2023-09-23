FROM python:3.9.13-alpine

WORKDIR /telegram-bot

COPY . .
RUN mkdir voice_message 

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["python3", "telegram_bot.py"]