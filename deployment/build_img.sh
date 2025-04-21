#!/bin/bash

set -ex;

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <image_version>"
    exit 1
fi

img_version="$1"
s_pwd="scraper123"

docker build --build-arg SCRAPER_PASS=$s_pwd  \
             -t localhost:5000/event_scraper:$img_version -f event_scraper/Dockerfile event_scraper
docker build -t localhost:5000/event_scraper_celery:$img_version -f event_scraper_celery/Dockerfile event_scraper_celery
docker build -t localhost:5000/event_scraper_rabbitmq:$img_version -f event_scraper_rabbitmq/Dockerfile event_scraper_rabbitmq
docker build -t localhost:5000/event_scraper_web:$img_version -f event_scraper_web/Dockerfile event_scraper_web
docker build -t localhost:5000/event_scraper_kafka:$img_version -f event_scraper_kafka/Dockerfile event_scraper_kafka
docker build -t localhost:5000/event_scraper_minio:$img_version -f event_scraper_minio/Dockerfile event_scraper_minio
