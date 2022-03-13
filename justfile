set dotenv-load := true

dco := "docker-compose"
run := "{{dco}} run --rm --entrypoint='' eduzenbot"

dco-version:
  {{dco}} --version

dockershell:
  {{run}}  eduzenbot bash

test:
  {{run}} pytest --cov=eduzen_bot

logs:
  {{dco}} logs -f eduzenbot

start:
  {{dco}} up -d
  logs

restart:
  {{dco}} rm -sf eduzenbot
  start

start-debug:
  {{dco}} run --rm --service-ports eduzenbot

clean:
  #!/usr/bin/env python3
  import pathlib, shutil
  current_path = pathlib.Path(".").parent
  [p.unlink() for p in current_path.rglob('*.py[co]')]
  [shutil.rmtree(p) for p in current_path.rglob('__pycache__')]
  [shutil.rmtree(p) for p in current_path.rglob('.pytest_cache')]
