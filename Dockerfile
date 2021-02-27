FROM ubuntu:20.04

COPY synex.py /bin/synex
COPY requirements.txt /tmp/requirements.txt
COPY synex.conf /etc/synex.conf

RUN apt-get update;\
    apt-get install -y python3-pip;\
    pip3 install -r /tmp/requirements.txt