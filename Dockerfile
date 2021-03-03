FROM ubuntu:20.04

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update;\
    apt-get install -y python3-pip;\
    pip3 install -r /tmp/requirements.txt

COPY synex.py /bin/synex
COPY synex.conf /etc/synex.conf
COPY couriers /usr/lib/python3/dist-packages/couriers
COPY handlers /usr/lib/python3/dist-packages/handlers