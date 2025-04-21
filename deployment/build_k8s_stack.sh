#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <image_version> (optional <--clean>)"
    exit 1
fi

registry="localhost:5000"
img_version="$1"

event_scraper_version="event_scraper:$img_version"
event_scraper_celery_version="event_scraper_celery:$img_version"
event_scraper_rabbitmq_version="event_scraper_rabbitmq:$img_version"
event_scraper_web_version="event_scraper_web:$img_version"
event_scraper_kafka_version="event_scraper_kafka:$img_version"
event_scraper_minio_version="event_scraper_minio:$img_version"

if [ "$2" == "--clean" ]; then
    echo "Cleaning up the Kubernetes stack..."
    bash clear_k8s_stack.sh
    echo "Waiting for 10s for graceful shutdown..."
    sleep 10
fi

echo "Pushing Docker images to private-registry..."
docker push $registry/$event_scraper_version 
docker push $registry/$event_scraper_celery_version 
docker push $registry/$event_scraper_rabbitmq_version 
docker push $registry/$event_scraper_web_version
docker push $registry/$event_scraper_kafka_version
docker push $registry/$event_scraper_minio_version

kubectl create namespace eventscraper 2>/dev/null
kubectl config set-context --current --namespace=eventscraper

sed -i 's/\(image:.*event_scraper_kafka.*\):.*$/\1:'$img_version'/' event_scraper_kafka/event_scraper_kafka.yaml 
sed -i 's/\(image:.*\):.*$/\1:'$img_version'/' event_scraper/event_scraper.yaml 
sed -i 's/\(image:.*\):.*$/\1:'$img_version'/' event_scraper_rabbitmq/event_scraper_rabbitmq.yaml 
sed -i 's/\(image:.*\):.*$/\1:'$img_version'/' event_scraper_celery/event_scraper_celery.yaml
sed -i 's/\(image:.*\):.*$/\1:'$img_version'/' event_scraper_web/event_scraper_web.yaml
sed -i 's/\(image:.*\):.*$/\1:'$img_version'/' event_scraper_minio/event_scraper_minio.yaml

kubectl apply -f event_scraper_kafka/event_scraper_kafka.yaml 
kubectl apply -f event_scraper/event_scraper.yaml
kubectl apply -f event_scraper_rabbitmq/event_scraper_rabbitmq.yaml 
kubectl apply -f event_scraper_celery/event_scraper_celery.yaml 
kubectl apply -f event_scraper_web/event_scraper_web.yaml 
kubectl apply -f event_scraper_minio/event_scraper_minio.yaml 

while true; do
    total_pods=$(kubectl get po | tail -n +2 | wc -l)
    total_pods=$((total_pods - 1))
    running_pods=$(kubectl get po --field-selector status.phase=Running | tail -n +2 | wc -l)
    echo "Pods running: $running_pods / $total_pods"

    if [ "$running_pods" -eq "$total_pods" ]; then
        echo "All pods are running."
        break
    fi

    echo "Non-running pods:"
    kubectl get po | grep -v "Running" | tail -n +2

    sleep 3
done

#
# Monitor
#
# watch "kubectl get po -o wide && echo && kubectl get svc && echo && kubectl get pv && echo && kubectl get pvc"

#
# Build & Run
#
# export EVT_SCRAPER_VERSION='4.9.8-1.0.1' && bash build_img.sh $EVT_SCRAPER_VERSION && bash build_k8s_stack.sh $EVT_SCRAPER_VERSION --clean

#
# Test
#
# kubectl exec $(kubectl get po | grep celery | awk '{print $1}') -- python -c "from tasks import run_scraper_task; run_scraper_task.delay()" && kubectl logs -f $(kubectl get po | grep celery | awk '{print $1}')

#
#
#
# kubectl logs -f $(kubectl get po | grep webserver | awk '{print $1}')

#
#
#
# kubectl exec $(kubectl get po | grep minio | awk '{print $1}') -- bash

kubectl exec $(kubectl get po | grep minio | awk '{print $1}') -- bash -c "\
    mc mb bucket-scraper-tasks && \
    mc ls bucket-scraper-tasks"

echo "Waiting for Kafka bootstrap server..."
kubectl wait --for=condition=complete job/create-kafka-topics --timeout=600s

echo "Kafka bootstrap server is up."
kubectl exec $(kubectl get po | grep kafka | awk '{print $1}' | tail -n +2) -- \
    kafka-topics.sh \
    --bootstrap-server kafka.eventscraper.svc.cluster.local:9092 \
    --list

#kubectl exec $(kubectl get po | grep kafka | awk '{print $1}' | tail -n +2) -- \
#    kafka-console-consumer.sh \
#    --bootstrap-server kafka.eventscraper.svc.cluster.local:9092 \
#    --topic scraped_data \
#    --from-beginning \
#    --timeout-ms 10000

echo "Deployment completed successfully."
exit 0
