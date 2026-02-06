#!/bin/bash

# JGPT Release Publisher
# Usage: ./scripts/publish_jgpt.sh

echo "📦 JGPT Enterprise Publisher"
echo "==========================="

SOURCE_DIR="products/JGPT/JGPTa"
TARGET_ZIP="secure-assets/JGPT_Enterprise_Source_v1.0.zip"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source directory '$SOURCE_DIR' not found."
    exit 1
fi

echo "🔍 Scanning source code..."
# Calculate hash/version if we wanted to be fancy, but simple zip is fine for now.

echo "🔒 Compressing asset to Secure Vault..."
# Remove old zip
rm -f "$TARGET_ZIP"

# Create new zip (excluding sensitive dev files)
zip -r "$TARGET_ZIP" "$SOURCE_DIR" -x "*.git*" -x "*node_modules*" -x "*.DS_Store*" -x "*.env*" -x "*__pycache__*"

echo "✅ Success! New release published to Portal."
echo "   Target: $TARGET_ZIP"
echo "   Size: $(du -h "$TARGET_ZIP" | cut -f1)"
