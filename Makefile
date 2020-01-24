.PHONY: test

kosei = docker-compose run kosei

clean:
	$(kosei) ash /code/docker/clean_virtualenv.sh

init: clean
	$(kosei) poetry install

style:
	$(kosei) isort **/*.py -c
	$(kosei) black --check .
	$(kosei) flake8

complexity:
	$(kosei) poetry run python -m mccabe --min 10 **/*.py

format:
	$(kosei) isort **/*.py
	$(kosei) black .

test:
	$(kosei) tox

test-unit:
	$(kosei) tox -e py38

shell:
	$(kosei) poetry shell

build:
	docker-compose build
