COMPOSE=docker-compose run --rm --entrypoint="" eduzenbot

build:
	docker-compose build

start:
	docker-compose up -d && docker-compose logs -f eduzenbot

restart:
	docker-compose down -v

test:
	${COMPOSE} pytest -v --cov=eduzen_bot

dockershell:
	${COMPOSE} bash

shell:
	${COMPOSE} ipython3

clean-python:
	rm -fr build
	rm -fr dist
	rm -fr __pycache__
	rm -fr *.egg-info
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;
