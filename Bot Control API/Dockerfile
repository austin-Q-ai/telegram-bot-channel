FROM docker:24.0.6-dind-alpine3.18

WORKDIR /bot_control_api

COPY . .

RUN apt-get -y install python3.9
RUN python3.9 -m pip install -r requirements.txt

EXPOSE 8080

CMD ["python3.9", "bot_control_api.py"]