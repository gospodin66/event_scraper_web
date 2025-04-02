#!/bin/bash

set -ex;

img_version="2.9"
s_pwd="scraper123"

docker build --build-arg SCRAPER_PASS=$s_pwd  \
             -t localhost:5000/event_scraper:$img_version -f event_scraper/Dockerfile event_scraper
docker build -t localhost:5000/event_scraper_celery:$img_version -f event_scraper_celery/Dockerfile event_scraper_celery
docker build -t localhost:5000/event_scraper_rabbitmq:$img_version -f event_scraper_rabbitmq/Dockerfile event_scraper_rabbitmq
docker build -t localhost:5000/event_scraper_web:$img_version -f event_scraper_web/Dockerfile event_scraper_web
