#!/bin/bash

# Try to find production configs before using default configs
# Check if production configuration file is available
PYRAMID_CONFIG_FILE="development-docker.ini"
PYRAMID_PROD_CONFIG="/configmaps/ini/pyramid_config.ini"
if [ -e "$PYRAMID_PROD_CONFIG" ]; then
    echo "Using configmap $PYRAMID_PROD_CONFIG"
    PYRAMID_CONFIG_FILE=$PYRAMID_PROD_CONFIG
fi

# Add host.docker.internal to /etc/hosts file for linux compatibility
HOST_DOMAIN="host.docker.internal"
HOST_IP=$(ip route | awk 'NR==1 {print $3}')
echo -e "$HOST_IP\t$HOST_DOMAIN" >> /etc/hosts

# Start pyramid server
gunicorn --paste "$PYRAMID_CONFIG_FILE" --bind=0.0.0.0:6543 --workers 2 --timeout 150