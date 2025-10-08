FROM python:3.14-slim-bookworm AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/code/.venv/bin:$PATH"

WORKDIR /code

RUN echo 'export PS1="\[\e[36m\]botshell>\[\e[m\] "' >> /root/.bashrc

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        iputils-ping \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        && \
    apt-get autoremove -y && \
    apt-get autoclean -y && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock /code/

RUN uv sync --frozen
COPY . .

CMD ["uv", "run", "python", "-m", "eduzenbot"]

FROM production AS dev

RUN uv sync --dev --frozen --all-groups --compile-bytecode

CMD ["uv", "run", "python", "-m", "eduzenbot"]
