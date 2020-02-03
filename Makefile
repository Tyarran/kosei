.PHONY: test

kosei = docker-compose run kosei
PYVERSION ?= py38

clean:
	$(kosei) ash /code/docker/clean_virtualenv.sh

init: clean
	$(kosei) poetry install

style:
	$(kosei) isort **/*.py -c
	$(kosei) black --check .
	$(kosei) flake8 --max-line-length=88

complexity:
	$(kosei) poetry run python -m mccabe --min 10 **/*.py

format:
	$(kosei) isort **/*.py
	$(kosei) black .

test:
	$(kosei) tox -e $(PYVERSION)

shell:
	$(kosei) poetry shell

build:
	docker-compose build
