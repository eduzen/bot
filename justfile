set dotenv-load := true

dco := "docker compose"
run := "docker compose run --rm eduzenbot"

check_env:
  #!/bin/bash
  if [ ! -f .env ]; then
    echo "Creating .env file from .env.sample"
    cp .env.sample .env
  fi

os:
  #!/usr/bin/env bash
  echo $OSTYPE

build: check_env
  #!/usr/bin/env bash
  {{dco}} build

dco-version:
  {{dco}} --version

dockershell:
  #!/usr/bin/env bash
  {{run}} eduzenbot bash

update-requirements-dev:
  {{run}} pip-compile --upgrade --extra=dev pyproject.toml -o requirements-dev.txt

update-requirements-prod:
  {{run}} pip-compile --upgrade pyproject.toml -o requirements.txt

update-requirements: check_env
  just update-requirements-dev
  just update-requirements-prod

test:
  {{run}} coverage run -m pytest

logs:
  {{dco}} logs -f eduzenbot

shell:
  {{run}} ipython

start: check_env
  {{dco}} up -d
  logs

restart:
  {{dco}} rm -sf eduzenbot
  start

start-debug: check_env
  {{dco}} run --rm --service-ports eduzenbot

install:
  python -m pip install -r requirements.txt

install-dev:
  python -m pip install -r requirements-dev.txt

compile:
  pip-compile pyproject.toml -o requirements.txt

compile-dev:
  pip-compile --extra=dev pyproject.toml -o requirements-dev.txt

format:
  uv run pre-commit run --all-files

fmt:
  just format

clean:
  #!/usr/bin/env python3
  import pathlib, shutil
  current_path = pathlib.Path('.').parent
  [p.unlink() for p in current_path.rglob('*.py[co]')]
  [shutil.rmtree(p) for p in current_path.rglob('__pycache__')]
  [shutil.rmtree(p) for p in current_path.rglob('.pytest_cache')]

run:
  uv run python -m eduzenbot

uv-test:
  uv run coverage run -m pytest

coverage:
  uv run coverage combine
  uv run coverage report
