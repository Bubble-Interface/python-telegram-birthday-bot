FROM python:3.10.2-slim-bullseye
WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY . .

RUN pip3 install -r requirements.txt

CMD [ "python", "main.py"]
