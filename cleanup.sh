#!/bin/bash

project_path=$(dirname "$0")

find "$project_path" -type f -name "*.log" -exec rm -f {} +
find "$project_path" -type d -name "__pycache__" -exec rm -rf {} +

echo "Cleanup done."
