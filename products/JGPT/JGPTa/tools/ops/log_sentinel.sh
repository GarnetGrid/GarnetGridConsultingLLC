#!/bin/bash
# log_sentinel.sh - Watch all logs, but make errors POP.

echo "👀 Sentinel is watching..."
echo "Filtering for: ERROR, EXCEPTION, FAIL, WARN"

# Trap Ctrl+C to exit gracefully
trap "exit" INT

# Tail docker logs, grep for coloring
# usage of grep colors: 31=red, 33=yellow
docker-compose logs -f --tail=100 | \
grep --line-buffered -E "ERROR|EXCEPTION|FAIL|WARN|$" | \
sed -E "s/(ERROR|EXCEPTION|FAIL)/$(printf '\033[31m')\1$(printf '\033[0m')/g" | \
sed -E "s/(WARN)/$(printf '\033[33m')\1$(printf '\033[0m')/g"
