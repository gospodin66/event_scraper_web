#!/bin/bash

set -ex;

registry="localhost:5000"
img_version="4.1"

event_scraper_version="event_scraper:$img_version"
event_scraper_celery_version="event_scraper_celery:$img_version"
event_scraper_rabbitmq_version="event_scraper_rabbitmq:$img_version"
event_scraper_web_version="event_scraper_web:$img_version"
event_scraper_kafka_version="event_scraper_kafka:$img_version"

docker push $registry/$event_scraper_version && \
docker push $registry/$event_scraper_celery_version && \
docker push $registry/$event_scraper_rabbitmq_version && \
docker push $registry/$event_scraper_web_version
docker push $registry/$event_scraper_kafka_version

kubectl create namespace eventscraper 2>/dev/null && \
kubectl config set-context --current --namespace=eventscraper

sed -i 's/\(image:.*event_scraper_kafka.*\):.*$/\1:'$img_version'/' event_scraper_kafka/event_scraper_kafka.yaml && \
sed -i 's/\(image:.*\):.*$/\1:'$img_version'/' event_scraper/event_scraper.yaml && \
sed -i 's/\(image:.*\):.*$/\1:'$img_version'/' event_scraper_rabbitmq/event_scraper_rabbitmq.yaml && \
sed -i 's/\(image:.*\):.*$/\1:'$img_version'/' event_scraper_celery/event_scraper_celery.yaml && \
sed -i 's/\(image:.*\):.*$/\1:'$img_version'/' event_scraper_web/event_scraper_web.yaml

kubectl apply -f event_scraper_kafka/event_scraper_kafka.yaml && \
kubectl apply -f event_scraper/event_scraper.yaml && \
kubectl apply -f event_scraper_rabbitmq/event_scraper_rabbitmq.yaml && \
kubectl apply -f event_scraper_celery/event_scraper_celery.yaml && \
kubectl apply -f event_scraper_web/event_scraper_web.yaml 

echo "Deployment completed successfully."
exit 0
