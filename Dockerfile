FROM python:3.10.2-slim-bullseye
WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
COPY birthday_bot.py birthday_bot.py
COPY service service
COPY models.py models.py


RUN pip3 install -r requirements.txt

CMD [ "python", "birthday_bot.py"]
