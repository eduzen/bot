*# Just another telegram-bot

```bash
  cargo install just
  just run
```

### Code style

For linting, code style and etcetera, we use [pre-commit](https://pre-commit.com/)

```bash
pre-commit install
pre-commit run --all-files
```

### Docker

for production `docker-compose.yaml`

```yaml
services:
  bot:
    image: index.docker.io/eduzen/bot:latest
    restart: always
    env_file:
      - .env
    volumes:
      - ./db.sqlite3:/code/db.sqlite3

  watchtower:
    image: index.docker.io/containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /home/eduzen/.docker/config.json:/config.json:ro
    command: --interval 30 --cleanup
```
*
