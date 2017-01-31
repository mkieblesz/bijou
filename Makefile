setup-system:
	@echo "--> Use latest version of Python"
	sudo add-apt-repository ppa:ubuntu-toolchain-r/test
	sudo add-apt-repository ppa:jonathonf/python-3.6
	sudo apt-get update

	@echo "--> Installing Python 3.6"
	sudo apt-get install python3.6 python3.6-dev
	sudo pip3 install virtualenv

	@echo "--> Install Redis for celery"
	sudo apt-get install redis

install-python:
	pip install -r requirements.txt

install-python-test:
	pip install -r requirements_test.txt

develop: install-python install-python-test

test: develop test-python

test-python:
	@echo "--> Testing python"
	.venv/bin/python manage.py test

test-python-coverage:
	@echo "--> Checking test coverage"
	coverage run --source=bijou -m .venv/bin/python manage.py test

lint: lint-python

lint-python:
	@echo "--> Linting python"
	flake8

coverage:
	make test-python-coverage
	coverage html

############
# Database #
############

reset-db:
	@echo "--> Dropping existing bijou database"
	rm bijou.db
	@echo "--> Creating bijou database"
	flask db init
