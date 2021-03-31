FROM python:latest
RUN apt update && apt install vim -y 
WORKDIR /opt/app
COPY ./requirements.txt /opt/app
RUN ls && pip3 install -r requirements.txt
COPY . /opt/app
CMD python3 -u bot.py
