FROM python:3.6-onbuild

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code:$PYTHONPATH

RUN mkdir /code
WORKDIR /code

RUN pip install --upgrade pip
COPY requirements-dev.txt requirements.txt /code/
RUN pip install -r requirements-dev.txt

COPY . /code/
RUN python setup.py develop
# RUN python -m textblob.download_corpora
