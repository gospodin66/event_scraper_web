#!/bin/bash

set -ex;

user=$(whoami)
export K3S_DATA_DIR="/home/k3s"
export INSTALL_K3S_SKIP_SELINUX_RPM=true 
export INSTALL_K3S_SKIP_START=true sudo mkdir -p /home/$user/.kube 2>/dev/null
sudo cp /etc/rancher/k3s/k3s.yaml /home/$user/.kube/config
sudo chown $user:$user /home/$user/.kube/config
sudo chmod 600 /home/$user/.kube/config

curl -sfL https://get.k3s.io | sh -s - server \
  --disable traefik \
  --disable-cloud-controller \
  --disable-network-policy \
  --data-dir "$K3S_DATA_DIR" \
  --write-kubeconfig-mode 644 \

#bash $(dirname $0)/private-registry.sh

sudo systemctl enable k3s
sudo systemctl start k3s

#sleep 10
sudo mkdir -p /home/$user/.kube 2>/dev/null
sudo cp /etc/rancher/k3s/k3s.yaml /home/$user/.kube/config
sudo chown $user:$user /home/$user/.kube/config
sudo chmod 600 /home/$user/.kube/config
