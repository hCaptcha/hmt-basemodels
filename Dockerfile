FROM ubuntu:bionic

WORKDIR /work
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y build-essential libffi-dev autoconf libtool \
    python3-dev python3-pip

ENV LANG C.UTF-8

COPY Pipfile Pipfile.lock /work/
RUN pip3 install pipenv
RUN pipenv install --system --deploy --dev

COPY test.py /work/
COPY basemodels /work/basemodels/
COPY bin /work/bin/

CMD sh
