#!/bin/bash
# port_killer.sh - When "Address already in use" ruins your day.
# Usage: ./port_killer.sh [PORT]

PORT=$1

if [ -z "$PORT" ]; then
    echo "Usage: ./port_killer.sh <PORT>"
    exit 1
fi

echo "🔫 Hunting for process on port $PORT..."

# Find PID (works on Mac/Linux)
PID=$(lsof -ti :$PORT)

if [ -z "$PID" ]; then
    echo "✅ No process found on port $PORT."
    exit 0
fi

echo "⚠️  Found PID: $PID"
ps -p $PID -o command=

read -p "Kill it? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill -9 $PID
    echo "💀 PID $PID has been terminated."
else
    echo "Mercy shown."
fi
