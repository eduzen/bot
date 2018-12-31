# Just another telegram-bot

## Installation

This project runs with `docker` (you can use traditional `virtualenv` but it's prepared out of the box for `docker`).
Also to manage docker, we are using [docker-compose](https://docs.docker.com/compose/).

## Create a keys file

```bash
touch keys.py
```

## Fill it with your twitter tokens

```python
TOKEN = 'some_token'
APP_ID = ''
TWITTER = {}
TWITTER["CONSUMER_KEY"] = 'consumer_key'
TWITTER["CONSUMER_SECRET"] = ""
TWITTER["ACCESS_TOKEN"] = ""
TWITTER["ACCESS_TOKEN_SECRET"] = "access_token_secret"
```

## Usage

If you already have `docker` and `docker-compose`, just run:

```bash
make start

# only test and flake8
make test
```

This command will download the images and build them in a container.

## Algunos commandos para pasarle a botfather

```json
cambio - Cotización de varias divisas
clima - Temperatura en baires
klima - Temperatura en München
dolar - Cotización del dolar
btc - Cotización del bitcoin
users - Lista de usuarios
add_question - Agrega una pregunta
edit_question - Editas una pregunta
add_answer - Agrega respuesta pasando Id
remove - Borra una pregunta
questions - Lista preguntas
question_menu - Menu de preguntas
caps - convierte a mayusculas
gasto - agrega un gasto
start - ayuda
code - Highlighted code
msg - Envia un msg privado
subte -  Estado del subte
subtenews - Estado del subte, acepta numero de tweets
transito -  Estado del transito
trenes -  Estado del trenes
set - Setear alarma
unset - Sacar alarma
qmenu - Menu para preguntas
restart - Reiniciar el bot
pull - Actualiza el codigo del bot
teatro - Lo mas buscado en AlternativaTeatral, acepta nro
dolarhoy - distintas cotizaciones
dolarfuturo - dolar futuro rofex
series - series para bajar
serie - serie para bajar
peli - buscar pelis
movie - buscar pelis
pelicula - buscar pelis
feriados - feriados en la argentina
```
