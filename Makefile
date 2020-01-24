.PHONY: test

style:
	docker-compose run kosei isort **/*.py -c
	docker-compose run kosei black --check .

format:
	docker-compose run kosei isort **/*.py
	docker-compose run kosei black .

test:
	docker-compose run kosei tox

test-unit:
	docker-compose run kosei tox -e py38
