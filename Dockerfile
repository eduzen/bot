FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /code:$PYTHONPATH

COPY requirements-dev.txt requirements.txt ./

RUN apk add --update --no-cache --virtual .build-deps \
    gcc \
    build-base \
    libffi-dev \
    openssl-dev && \
    pip install --no-cache-dir -r requirements_dev.txt && \
    find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' +

WORKDIR /code
COPY . /code

RUN python setup.py develop
