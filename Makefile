test:
	docker-compose run --rm eduzenbot pytest --cov=eduzenbot --cov-report=term-missing

dockershell:
	docker-compose run --rm eduzenbot bash
