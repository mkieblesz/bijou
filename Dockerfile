FROM ubuntu:14.04

WORKDIR /app
COPY . /app
RUN apt-get update && \
    apt-get install -y build-essential

RUN apt-get install -y software-properties-common python-software-properties

RUN make setup && \
    make develop && \
    virtualenv -p python3.6 .venv && \
    source .venv/bin/activate && \
    make develop && \
    make reset-db && \
    make runserver

EXPOSE 5000

CMD false