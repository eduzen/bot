FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONPATH /code:$PYTHONPATH
RUN echo 'export PS1="\[\e[36m\]botshell>\[\e[m\] "' >> /root/.ashrc

COPY requirements-dev.txt requirements.txt ./

RUN apk add --update --no-cache --virtual .build-deps \
    gcc \
    build-base \
    libffi-dev \
    openssl-dev && \
    pip install --no-cache-dir -r requirements-dev.txt && \
    find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' +

WORKDIR /code
COPY . /code

RUN python setup.py develop
CMD ["python3", "eduzen_bot", "-v"]
