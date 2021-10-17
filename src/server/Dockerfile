FROM python:3.10-buster

WORKDIR /app

RUN apt-get update && apt-get upgrade -y

COPY ./server/* /app/

COPY ./common/* /app/common/

RUN pip3 install bottle mongoengine

EXPOSE 8080

CMD [ "python3", "main.py" ]