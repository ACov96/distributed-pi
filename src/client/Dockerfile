
FROM python:3.10-buster

WORKDIR /app

RUN apt-get update && apt-get upgrade -y

COPY ./client/* /app/

COPY ./common/* /app/common/

RUN pip3 install requests

CMD [ "python3", "main.py" ]