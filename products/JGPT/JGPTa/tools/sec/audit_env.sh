#!/bin/bash
# audit_env.sh - Checks if your .env file is missing keys from .env.example

EXAMPLE_FILE=".env.example"
REAL_FILE=".env"

print_red() { echo -e "\033[31m$1\033[0m"; }
print_green() { echo -e "\033[32m$1\033[0m"; }

if [ ! -f "$EXAMPLE_FILE" ]; then
    print_red "Error: $EXAMPLE_FILE not found."
    exit 1
fi

if [ ! -f "$REAL_FILE" ]; then
    print_red "Error: $REAL_FILE not found."
    exit 1
fi

echo "🔍 Auditing $REAL_FILE against $EXAMPLE_FILE..."
MISSING=0

# Loop through lines in example
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    if [[ $line =~ ^#.* ]] || [[ -z $line ]]; then
        continue
    fi
    
    # Extract key
    KEY=$(echo "$line" | cut -d '=' -f 1)
    
    # Check if key exists in real file
    if ! grep -q "^$KEY=" "$REAL_FILE"; then
        print_red "MISSING: $KEY"
        MISSING=$((MISSING+1))
    fi
done < "$EXAMPLE_FILE"

if [ $MISSING -eq 0 ]; then
    print_green "✅ All keys present."
else
    print_red "❌ Found $MISSING missing keys."
    exit 1
fi
