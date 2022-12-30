FROM python:3.11-slim-bullseye as production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONWARNINGS='ignore:Unverified HTTPS request'

WORKDIR /code

RUN echo 'export PS1="\[\e[36m\]botshell>\[\e[m\] "' >> /root/.bashrc

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        iputils-ping \
        libpq-dev \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        && \
    apt-get autoremove -y && \
    apt-get autoclean -y && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -U wheel pip

COPY pyproject.toml requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .

CMD ["python", "eduzenbot"]

FROM production as dev

RUN pip install --no-cache-dir -r requirements-dev.txt -e .

CMD ["python", "eduzenbot"]
