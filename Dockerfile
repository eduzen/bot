FROM python:3.6-stretch

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code:$PYTHONPATH

WORKDIR /code

COPY requirements-dev.txt requirements.txt /code/
RUN pip install -r requirements-dev.txt

COPY . /code/
RUN python setup.py develop
