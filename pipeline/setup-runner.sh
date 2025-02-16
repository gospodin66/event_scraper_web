#!/bin/bash

docker stop github-runner; docker rm github-runner
docker build -t github-runner .

docker run -d \
           -e REPO_URL="https://github.com/gospodin66/event_scraper_web" \
           --mount type=bind,source=$(pwd)/.runner-token.txt,target=/home/runner/.runner-token.txt \
           --name github-runner \
           github-runner

exit 0
