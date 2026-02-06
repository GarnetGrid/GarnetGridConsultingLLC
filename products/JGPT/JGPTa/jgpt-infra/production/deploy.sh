#!/bin/bash
set -e

# JGPT Production Deployment Script ("The Fortress") -> deploy.sh

echo "Deploying JGPT Fortress..."

# 1. Pull latest code
git pull origin main

# 2. Build and start containers
# We use the production compose file
docker-compose -f jgpt-infra/production/docker-compose.prod.yml down
docker-compose -f jgpt-infra/production/docker-compose.prod.yml up -d --build

echo "Deployment complete. Checking status..."
docker-compose -f jgpt-infra/production/docker-compose.prod.yml ps

echo "JGPT is live."
