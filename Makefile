test:
	docker-compose run --rm eduzenbot pytest --cov=eduzenbot --cov-report=term-missing

dockershell:
	docker-compose run --rm eduzenbot bash

compile:
	pip-compile pyproject.toml -o requirements.txt

compile-dev:
	pip-compile --extra=dev pyproject.toml -o requirements-dev.txt

coverage:
	TOKEN=blah EDUZEN_ID=9 coverage run -m pytest
	python -m coverage combine
	python -m coverage report -m --skip-covered
	python -m coverage json
