#!/bin/bash

docker stop github-runner; docker rm github-runner
docker build -t github-runner .
docker run -d \
           -e REPO_URL="https://github.com/gospodin66/event_scraper_web" \
           --mount type=bind,source=$(pwd)/.runner-token.txt,target=/home/runner/.runner-token.txt \
           --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
           --mount type=bind,source=/usr/bin/docker,target=/usr/bin/docker \
           --name github-runner \
           github-runner
exit 0
