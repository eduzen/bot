test:
	docker-compose run --rm eduzenbot pytest --cov=eduzenbot --cov-report=term-missing

dockershell:
	docker-compose run --rm eduzenbot bash

compile:
	pip-compile pyproject.toml -o requirements.txt

compile-dev:
	pip-compile --all-extras pyproject.toml -o requirements-dev.txt

format:
	pre-commit run --all-files

upgrade:
	uv pip compile --upgrade pyproject.toml -o requirements.txt

upgrade-dev:
	uv pip compile --upgrade --all-extras pyproject.toml -o requirements-dev.txt
