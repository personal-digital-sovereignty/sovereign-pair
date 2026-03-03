#!/bin/bash

echo "Starting automated retry deployment for Sovereign Coder Node (Oracle Free Tier)..."
echo "It will attempt to run 'tofu apply' every 2 minutes until successful."

while true; do
    echo "========================================"
    echo "Attempting deployment at $(date)..."
    tofu apply -auto-approve
    
    if [ $? -eq 0 ]; then
        echo "========================================"
        echo "Deployment successful at $(date)!"
        echo "Exiting retry loop."
        break
    else
        echo "Deployment failed (likely Out of host capacity). Retrying in 120 seconds..."
        sleep 120
    fi
done
