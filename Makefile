help:
	@echo "help  -- print this help"
	@echo "build -- build bot"
	@echo "start -- start docker stack (and rebuild) detached"
	@echo "up 	 -- up docker container"
	@echo "stop  -- stop docker stack"
	@echo "ps    -- show status"
	@echo "clean -- clean all artifacts"
	@echo "test  -- run tests using docker"
	@echo "dockershell -- bash shell inside of docker"
	@echo "shell -- run ipython shell"
	@echo "clean-python -- clean all python cache and stuff"


COMPOSE = docker-compose run --rm --entrypoint="" eduzenbot

build:
	docker-compose build

start-build: clean
	docker-compose up --build -d

up:
	docker-compose up -d

start:
	docker-compose up

stop:
	docker-compose stop

ps:
	docker-compose ps

clean: stop
	docker-compose rm --force -v

test:
	docker-compose run --rm --entrypoint="" eduzenbot pytest

flake8:
	docker-compose run --rm eduzenbot flake8 .

dockershell:
	${COMPOSE} bash

shell:
	docker-compose run --rm eduzenbot ipython3

clean-python:
	rm -fr build
	rm -fr dist
	rm -fr __pycache__
	rm -fr *.egg-info
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

.PHONY: help start up stop ps clean test dockershell shell only_test pep8 clean-python
