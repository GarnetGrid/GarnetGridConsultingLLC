#!/bin/bash

# JGPT Smart Reboot & Auditing System
# =================================
# This script performs a clean restart of the JGPT ecosystem to ensure
# all code changes are reflected and the system is fully operational.

echo "🔄 JGPT Smart Reboot Protocol Initiated..."

# 1. Cleanup
echo "🧹 Cleaning up system state..."
# Kill any lingering local python processes that might conflict (optional, mostly for dev)
pkill -f "uvicorn app.main:app" || true
# Remove pycache to prevent stale bytecode issues
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "   - Caches cleared."

# 2. Docker Reset
echo "🐳 Resetting Docker containers..."
echo "   - Stopping services..."
docker-compose down

echo "   - Rebuilding and Starting (forcing recreation)..."
# --build forces a rebuild of the image to include new code layers
# --force-recreate ensures containers are fresh
docker-compose up -d --build --force-recreate

# 3. Health Wait Loop
echo "⏳ Waiting for API to stabilize..."
MAX_RETRIES=30
COUNT=0
URL="http://localhost:8000/api/health"

while [ $COUNT -lt $MAX_RETRIES ]; do
    if curl -s "$URL" | grep -q '{"ok":true}'; then
        echo "   ✅ API is up and healthy!"
        break
    fi
    echo "   - Waiting for healthcheck ($((COUNT+1))/$MAX_RETRIES)..."
    sleep 2
    COUNT=$((COUNT+1))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Timeout waiting for API health."
    exit 1
fi

# 4. Verification
echo "🔍  Running System Audit..."
if [ -f "audit_system.py" ]; then
    python3 audit_system.py
else
    echo "⚠️  Audit script not found in current directory."
fi

echo "========================================"
echo "🚀 Reboot Complete."
