#!/bin/bash

docker build -t event_scraper_minio .

docker run -d --name event-scraper-minio \
  -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  -v /home/cheki/workspace/event_scraper_web/event_scraper_minio/bucket_scraper_tasks:/data/bucket_scraper_tasks \
  -v /home/cheki/workspace/event_scraper_web/event_scraper_minio/bucket_tasks:/data/bucket_tasks \
  custom-minio