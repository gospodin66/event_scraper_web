#!/bin/bash

namespace="eventscraper"
context="default"

kubectl config set-context --current --namespace=$namespace

resources=( "deploy" "cm" "secret" "svc" "pvc" "pv" "job" )

echo "Deleting resources $resources in $namespace namespace..."

for resource in "${resources[@]}"; do
    kubectl delete $resource $(kubectl get $resource | awk '{print $1}' | tail -n +2)
done

echo "Cluster cleaned up successfully."