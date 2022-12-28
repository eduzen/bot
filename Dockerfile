FROM python:3.10-slim-bullseye as production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONWARNINGS='ignore:Unverified HTTPS request'

RUN echo 'export PS1="\[\e[36m\]botshell>\[\e[m\] "' >> /root/.ashrc

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        gettext \
        curl \
        iputils-ping \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        build-essential \
        postgresql-client && \
    apt-get autoremove -y && \
    apt-get autoclean -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY pyproject.toml requirements.txt ./

RUN pip install wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .

CMD ["python", "eduzenbot"]

FROM production as dev

RUN pip install wheel && \
    pip install --no-cache-dir -r requirements-dev.txt -e .

CMD ["python", "eduzenbot"]
