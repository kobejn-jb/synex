# syntax=docker/dockerfile:1
FROM ubuntu:20.04 as base

# Never prompts the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update\
    && apt-get install -y python3-pip rsync\
    && pip3 install -r /tmp/requirements.txt\
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

ENV PYTHONPATH=/opt/synex

FROM base as release

COPY synex/synex.py /bin/synex
COPY synex.conf /etc/synex.conf
COPY synex/couriers /usr/lib/python3/dist-packages/couriers
COPY synex/handlers /usr/lib/python3/dist-packages/handlers

FROM base as test

ARG UID=1000
ARG GID=1000

COPY requirements-test.txt /tmp/requirements-test.txt
RUN pip3 install -r /tmp/requirements-test.txt

RUN groupadd -g ${GID} developer && \
    useradd developer -m -s /bin/bash -d /home/developer -g ${GID} -u ${UID} && \
    chown -R developer:developer /home/developer && \
    echo "developer  ALL=(ALL)  NOPASSWD:ALL" >> etc/sudoers && \
    echo 'developer:developer' | chpasswd
USER developer

WORKDIR /opt/synex