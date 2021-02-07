# Just another telegram-bot
## Algunos commandos para pasarle a botfather

```json
cambio - Cotización de varias divisas
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
dolarhoy - distintas cotizaciones
dolarfuturo - dolar futuro rofex
series - series para bajar
serie - serie para bajar
peli - buscar pelis
movie - buscar pelis
pelicula - buscar pelis
feriados - feriados en la argentina
time - hora en algun lugar
```


for roduction `docker-compose.yaml`

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
