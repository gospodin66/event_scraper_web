#!/bin/bash

set -ex;

if [ -z "$REPO_URL" ]; then
    echo "Error: REPO_URL environment variable is not set."
    exit 1
fi

hash="b13b784808359f31bc79b08a191f5f83757852957dd8fe3dbfcc38202ccf5768"

mkdir actions-runner; cd actions-runner
curl -o actions-runner-linux-x64-2.322.0.tar.gz \
     -L https://github.com/actions/runner/releases/download/v2.322.0/actions-runner-linux-x64-2.322.0.tar.gz

echo "$hash  actions-runner-linux-x64-2.322.0.tar.gz" | shasum -a 256 -c
tar xzf ./actions-runner-linux-x64-2.322.0.tar.gz

./config.sh --url $REPO_URL --token $(cat /home/runner/.runner-token.txt)
./run.sh

exit 0