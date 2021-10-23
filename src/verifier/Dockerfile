
FROM python:3.10-buster

EXPOSE 8080

RUN apt-get update && apt-get upgrade -y

RUN pip3 install mongoengine bottle

WORKDIR /app

COPY ./verifier/* /app/

COPY ./common/* /app/common/

CMD [ "python3", "main.py" ]