help:
	@echo "help  -- print this help"
	@echo "build -- build bot"
	@echo "start -- start docker stack"
	@echo "stop  -- stop docker stack"
	@echo "ps    -- show status"
	@echo "clean -- clean all artifacts"
	@echo "test  -- run tests using docker"
	@echo "dockershell -- bash shell inside of docker"
	@echo "bootstrap --build containers, run django migrations, load fixtures and create the a superuser"

build:
	docker-compose build

start: clean
	docker-compose up --build

stop:
	docker-compose stop

ps:
	docker-compose ps

clean: stop
	docker-compose rm --force -v

only_test: build
	docker-compose run --rm eduzenbot pytest --cov=. --cov-config setup.cfg

pep8:
	docker-compose run --rm eduzenbot flake8 .

test: build pep8 only_test

dockershell:
	docker-compose run --rm eduzenbot bash

.PHONY: help start stop ps clean test dockershell shell_plus only_test pep8
