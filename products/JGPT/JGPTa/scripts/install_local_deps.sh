#!/usr/bin/env bash
set -euo pipefail
echo "Installing local Python deps for JGPT web ingestion scripts..."
python3 -m pip install --upgrade pip
python3 -m pip install -r scripts/requirements.txt
echo "Done."
