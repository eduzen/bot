set dotenv-load := true

dco := "docker-compose"
run := "{{dco}} run --rm --entrypoint='' eduzenbot"

os:
  #!/usr/bin/env bash
  echo $OSTYPE

dco-version:
  {{dco}} --version

dockershell:
  {{run}}  eduzenbot bash

test:
  {{run}} pytest --cov=eduzenbot

logs:
  {{dco}} logs -f eduzenbot

shell:
  {{run}} ipython

start:
  {{dco}} up -d
  logs

restart:
  {{dco}} rm -sf eduzenbot
  start

start-debug:
  {{dco}} run --rm --service-ports eduzenbot

install:
  python -m pip install -r requirements.txt

install-dev:
  python -m pip install -r requirements-dev.txt

compile:
  pip-compile pyproject.toml -o requirements.txt

compile-dev:
  pip-compile --extra=dev pyproject.toml -o requirements-dev.txt

clean:
  #!/usr/bin/env python3
  import pathlib, shutil
  current_path = pathlib.Path(".").parent
  [p.unlink() for p in current_path.rglob('*.py[co]')]
  [shutil.rmtree(p) for p in current_path.rglob('__pycache__')]
  [shutil.rmtree(p) for p in current_path.rglob('.pytest_cache')]
