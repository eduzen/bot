FROM python:3.6-onbuild

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code:$PYTHONPATH

RUN mkdir /code
WORKDIR /code

COPY requirements-dev.txt requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/
RUN python setup.py develop
