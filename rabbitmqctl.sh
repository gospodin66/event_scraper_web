#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Error: Script should be ran as root."
    exit 1
fi

cmds=(
    "list_bindings"
    "list_channels"
    "list_ciphers"
    "list_connections"
    "list_consumers"
    "list_exchanges"
    "list_hashes"
    "list_node_auth_attempt_stats"
    "list_queues"
    "list_unresponsive_queues"
)

for cmd in ${cmds[@]}; do
    rabbitmqctl $cmd
    echo -e "\n\n"
done

exit 0