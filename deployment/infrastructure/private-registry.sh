#!/bin/bash

set -ex;

REGISTRY_CONTAINER="private-registry"
REGISTRY_PORT="5000"
REGISTRY_DIR="/home/registry"
K3S_DIR="/home/k3s"
K3S_REGISTRY_CONFIG="/etc/rancher/k3s/registries.yaml"

if ! systemctl is-active --quiet docker; then
  echo "Docker is not running. Starting it..."
  sudo systemctl start docker
fi

docker run -d --restart=always --name $REGISTRY_CONTAINER -p $REGISTRY_PORT:5000 \
  -v $REGISTRY_DIR:/var/lib/registry \
  -v ./registry.yaml:/etc/docker/registry/config.yml \
  registry:2 || echo "Registry already running"

# Add an insecure registry configuration for crane
export crane_insecure=true

sudo mkdir -p /etc/rancher/k3s $K3S_DIR
sudo chown -R root:root $K3S_DIR && \
sudo chmod 755 $K3S_DIR

cat <<EOF | sudo tee $K3S_REGISTRY_CONFIG
mirrors:
  "localhost:$REGISTRY_PORT":
    endpoint:
      - "http://localhost:$REGISTRY_PORT"
EOF

if ! command -v crane &> /dev/null; then
  echo "Installing crane..."
  curl -sSL https://github.com/google/go-containerregistry/releases/latest/download/go-containerregistry_Linux_x86_64.tar.gz | sudo tar -xz -C /usr/local/bin crane
  if ! command -v crane &> /dev/null; then
    echo "Crane installation failed!" >&2
    exit 1
  fi
fi

docker ps | grep $REGISTRY_CONTAINER || echo "Registry container is not running!"
crane catalog --insecure localhost:$REGISTRY_PORT || true 

echo "Private registry setup complete!"
