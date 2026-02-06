#!/bin/bash
# docker_reimagine.sh - When "docker-compose up" just isn't listening.
# Usage: ./docker_reimagine.sh [service_name]

SERVICE=$1

echo "🎨 REIMAGINING DOCKER INFRASTRUCTURE..."

if [ -z "$SERVICE" ]; then
    echo "Target: ENTIRE STACK"
    
    echo "Stopping all containers..."
    docker-compose down --remove-orphans

    echo "Pruning docker system (force)..."
    # Be careful with system prune in shared envs, but for dev tools it's often needed
    # docker system prune -f 
    
    echo "Rebuilding..."
    docker-compose up -d --build
else
    echo "Target: Service '$SERVICE'"
    
    echo "Stopping $SERVICE..."
    docker-compose stop $SERVICE
    docker-compose rm -f $SERVICE
    
    echo "Rebuilding $SERVICE..."
    docker-compose up -d --build $SERVICE
fi

echo "🚀 Launch sequence complete."
docker-compose ps
