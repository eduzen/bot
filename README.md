# Just another telegram-bot

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

## Create a keys file

```bash
touch keys.py
```
## Fill it with your token

```python
TOKEN = 'some_token'
APP_ID = ''
TWITTER = {}
TWITTER["CONSUMER_KEY"] = 'consumer_key'
TWITTER["CONSUMER_SECRET"] = ""
TWITTER["ACCESS_TOKEN"] = ""
TWITTER["ACCESS_TOKEN_SECRET"] = "access_token_secret"
```

## Algunos commandos para pasarle a botfather
```
cambio - Cotización de varias divisas
clima - Temperatura en baires
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
```
