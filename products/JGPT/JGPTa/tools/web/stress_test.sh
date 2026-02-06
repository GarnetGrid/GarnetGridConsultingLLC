#!/bin/bash
# stress_test.sh - "How much can it take?" using ab (Apache Bench)
# Usage: ./stress_test.sh [URL] [REQUESTS] [CONCURRENCY]

URL=${1:-"http://localhost:3000/"}
[[ "${URL}" != */ ]] && URL="${URL}/"
REQUESTS=${2:-100}
CONCURRENCY=${3:-10}

echo "🔥 STRESS TEST INITIATED 🔥"
echo "Target: $URL"
echo "Requests: $REQUESTS"
echo "Concurrency: $CONCURRENCY"

if command -v ab &> /dev/null; then
    echo "Using Apache Bench (ab)..."
    ab -n $REQUESTS -c $CONCURRENCY $URL
else
    echo "⚠️  Apache Bench (ab) not found. Falling back to simple curl loop..."
    START=$(date +%s)
    
    for ((i=1;i<=REQUESTS;i++)); do
        curl -s -o /dev/null -w "%{http_code}\n" $URL &
        if (( i % CONCURRENCY == 0 )); then wait; fi
    done
    wait
    
    END=$(date +%s)
    echo "Done in $((END-START)) seconds."
fi
