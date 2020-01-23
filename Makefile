.PHONY: test

test:
	docker-compose run kosei tox

test-unit:
	docker-compose run kosei tox -e py38
