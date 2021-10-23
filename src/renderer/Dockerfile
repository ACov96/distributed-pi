FROM python:3.10-buster

EXPOSE 8080

RUN apt-get update && apt-get upgrade -y

RUN pip3 install mongoengine bottle tqdm

WORKDIR /app

COPY ./renderer/* /app/

COPY ./common/* /app/common/

CMD [ "python3", "main.py" ]