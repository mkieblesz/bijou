# Bijou

Bijou is Tinder for commerce.

## Instalation

Run `make setup` to setup system requirements (tested on Ubuntu 14.04). If you are using mac please install system
requirements manually or setup Vagrant machine.

Setup and activate virtual environment by running `virtualenv -p python3.6 .venv && source .venv/bin/activate`. Then
run `make develop` to setup development environment.

Now create database `make reset-db` and run `make runserver` to start development server.

## Excercise

Run `make scrape` to scrape farah.co.uk shop - it might take up to 30 min.

Run `make runserver` and navigate to http://localhost:5000/shop_product and http://localhost:5000/shop_category to
see product and category data. If you want to see individual object go to http://localhost:5000/shop_product/{id} and
http://localhost:5000/shop_category/{id}.


## Question

What not to store?
- categories which are just filters upon product special types (sale, new, classic)
- availability of products for different colors/sizes (this data will need to be retrieved dynamically, this is not
    type of data which is for scraping)

What to store?
- data which will be displayed on swipe page and on swipe details page
- products may have multiple categories so it would be good to have many to many
- url so we can refresh specific page and not checking whole site (we could scrape most used products more frequenly
    visited than less frquently visited), this is one of the reasons why having each scraper for each data type to
    scrape, another is we can spin up workers which will hit with as much concurrency as we want)
- colors and sizes in JSON field (postgres is quick in filtering those and it simplifies things a lot), to diplay
    filters like on farah on category we will just need to aggregate
- colors should contain image urls of a product
- promotion stuff so we can create our own sale filter category (also product's price before promotion)
- common tag (when scraping other websites we would want to have same/very similar types of categories under tag model)

## Testing

Run `make test` to run testing suite.

## Todo

This is default stuff which should be done in project like this.

- more tests!
- run run method of scrapers as celery task (upon creating instead put it on queue and workers will evoke run method)
- one celery scheduled task which loops through all sites scrapers every 5 min and checks it should be rescraped
    (depending on time, depth of scraping etc.)
- better error handling in scraper parsers
- write browser method scraper - for some sites just https requesting won't work
- write better serialization/filtering models by using get parameters via model endpoint (or use 3rd party like
    flask-restful)
- write provisioning scripts for each tst/dev/stg/prd and mgt envs
- write vagrant script for devs
- web view should be small (just few pages, with client framework of choices which will use api)
- put vcr into s3 or directly to git so when testing in CI it runs without hitting websites and option to run tests
    online (without using vcr)
- use sentry for logging
- better application logging
- write swiping stuff endpoint
- registration/login/account management using flask_user and additionally endpoints for mobile apps
- write payment stuff
- add admin panel
- more
