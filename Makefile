################
# System setup #
################

setup-system:
	@echo "--> Update repos used in this project"
	sudo add-apt-repository ppa:ubuntu-toolchain-r/test
	sudo add-apt-repository ppa:jonathonf/python-3.6
	sudo apt-get update

	@echo "--> Updating C compilers to 4.9 and add libpq-dev (for psycopg2 to compile)"
	sudo apt-get install build-essential git libpq-dev gcc-4.9 cpp-4.9 g++-4.9
	sudo rm /usr/bin/gcc /usr/bin/cpp /usr/bin/x86_64-linux-gnu-gcc
	sudo ln -s /usr/bin/gcc-4.9 /usr/bin/x86_64-linux-gnu-gcc
	sudo ln -s /usr/bin/gcc-4.9 /usr/bin/gcc
	sudo ln -s /usr/bin/cpp-4.9 /usr/bin/cpp

	@echo "--> Installing Python 3.6"
	sudo apt-get install python3.6 python3.6-dev
	sudo pip3 install virtualenv

	@echo "--> Install Redis for celery"
	sudo apt-get install redis-server

setup-db:
	@echo "--> Setting up postgres"
	sudo apt-get install postgresql
	sudo -H -u postgres bash -c "createuser --superuser $USER"
	sudo psql -c "CREATE ROLE bijou WITH PASSWORD 'bijou' CREATEDB LOGIN;"

setup: setup-system setup-db

#############
# Dev setup #
#############

install-python:
	pip install -r requirements.txt

install-python-test:
	pip install -r requirements_test.txt

develop: install-python install-python-test

###############
# Development #
###############

runserver:
	.venv/bin/python manage.py runserver

rungunicornserver:
	.venv/bin/gunicorn wsgi --bind 127.0.0.1:5001 -w 5 --threads 5

###########
# Testing #
###########

test: test-python

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
	@echo "--> Dropping existing 'bijou' database"
	dropdb bijou || true
	@echo "--> Creating 'bijou' database"
	PGPASSWORD=bijou createdb -E utf-8 bijou
	.venv/bin/python manage.py init_db

############
# Scraping #
############

scrape:
	.venv/bin/python manage.py scrape
