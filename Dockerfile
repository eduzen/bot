FROM python:3.13-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/code/.venv/bin:$PATH"

WORKDIR /code

# Nice shell prompt for interactive shells
RUN echo 'export PS1="\[\e[36m\]botshell>\[\e[m\] "' >> /root/.bashrc


# ---- Builder for production dependencies (no dev tools) ----
FROM base AS builder

# Build dependencies only in builder stage
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        gcc \
        build-essential \
        pkg-config \
        libffi-dev \
        && \
    rm -rf /var/lib/apt/lists/*

# Install uv and resolve dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen


# ---- Minimal runtime image ----
FROM base AS production

# Copy only the resolved virtualenv and the app code
COPY --from=builder /code/.venv /code/.venv
COPY . .

# Runtime shared libraries required by compiled wheels (e.g., cffi)
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        libffi8 \
        && \
    rm -rf /var/lib/apt/lists/*

# Run with the virtualenv Python directly (no uv needed at runtime)
CMD ["/code/.venv/bin/python", "-m", "eduzenbot"]


# ---- Dev image with extra tools & dev dependencies ----
FROM base AS dev

# Dev tools only (kept out of production)
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        iputils-ping \
        gcc \
        build-essential \
        pkg-config \
        libffi-dev \
        && \
    rm -rf /var/lib/apt/lists/*

# uv for interactive workflows in dev
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock /code/
RUN uv sync --dev --frozen --all-groups
COPY . .

CMD ["uv", "run", "python", "-m", "eduzenbot"]
