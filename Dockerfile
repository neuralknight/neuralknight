FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y git && \
    python3 -m pip install --upgrade pip setuptools

# We copy this file first to leverage docker cache
COPY ./requirements.txt /app/requirements.txt
COPY ./docker.ini /app/docker.ini

WORKDIR /app

RUN pip3 install -r requirements.txt
# COPY . /app

RUN pserve docker.ini
ENTRYPOINT [ "/bin/bash" ]

CMD [ "pserve docker.ini" ]
