# Just another telegram-bot

![test](https://github.com/eduzen/bot/actions/workflows/test.yml/badge.svg)
![docker](https://github.com/eduzen/bot/actions/workflows/docker-publish.yml/badge.svg)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)

![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/eduzen/939569bc7abab34a443758333f60764d/raw/covbadge.json)

We use [just](https://github.com/casey/just) to run our project-specific commands. Under the hood, it uses docker to run our bot.
So you will need docker too. Secrets are handle by `.env` file. So you will need to copy `.env.example` to `.env` and fill it with your secrets.


```bash
  cargo install just
  cp .env.sample .env
  just start
```

### Code style

For linting, code style and etcetera, we use [pre-commit](https://pre-commit.com/)

```bash
pre-commit install
pre-commit run --all-files
```

### Dependencies

We are using poetry. So in case you need a new library just run:

```bash
docker-compose run --entrypoint="" --rm eduzenbot poetry add astral
```

## Algunos commandos para pasarle a botfather

```json
config_reporte - config crypto reporte
usage - uso del bot
clima - Temperatura en baires
klima - Temperatura en München
dolar - Cotización del dolar
btc - Cotización del bitcoin
stock - Cotizacion de acciones
users - Lista de usuarios
subte -  Estado del subte
subtenews - Estado del subte, acepta numero de tweets
transito -  Estado del transito
trenes -  Estado del trenes
restart - Reiniciar el bot
teatro - Lo mas buscado en AlternativaTeatral, acepta nro
series - series para bajar
serie - serie para bajar
peli - buscar pelis
movie - buscar pelis
pelicula - buscar pelis
feriados - feriados en la argentina
time - hora en algun lugar
```


for production `docker-compose.yaml`

```
version: "3.8"

volumes:
  pgdata:

services:
  bot:
    image: index.docker.io/eduzen/bot:latest
    restart: always
    env_file:
      - .env
    volumes:
      - pgdata:/var/lib/postgresql/data/
  db:
    image: index.docker.io/postgres:13-alpine
    restart: always
    env_file:
      - .env
    volumes:
      - pgdata:/var/lib/postgresql/data/

  watchtower:
    image: index.docker.io/containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /home/eduzen/.docker/config.json:/config.json:ro
    command: --interval 30 --cleanup
```
