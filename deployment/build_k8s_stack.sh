#!/bin/bash

set -ex;

registry="localhost:5000"
img_version="2.9"

event_scraper_version="event_scraper:$img_version"
event_scraper_celery_version="event_scraper_celery:$img_version"
event_scraper_rabbitmq_version="event_scraper_rabbitmq:$img_version"
event_scraper_web_version="event_scraper_web:$img_version"

docker push $registry/$event_scraper_version && \
docker push $registry/$event_scraper_celery_version && \
docker push $registry/$event_scraper_rabbitmq_version && \
docker push $registry/$event_scraper_web_version

kubectl create namespace eventscraper && \
kubectl config set-context --current --namespace=eventscraper

kubectl apply -f event_scraper/event_scraper.yaml && \
kubectl apply -f event_scraper_celery/event_scraper_celery.yaml && \
kubectl apply -f event_scraper_rabbitmq/event_scraper_rabbitmq.yaml && \
kubectl apply -f event_scraper_web/event_scraper_web.yaml
