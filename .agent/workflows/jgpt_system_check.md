description: Check Yourself - JGPT System Diagnostic
---
# Check Yourself - System Diagnostic

This workflow runs a diagnostic script to verify the health of all JGPT components.

## Steps

1. Run the master diagnostic script.
// turbo
2. bash /Users/Anonymous/Downloads/GarnetGridConsultingLLC-website/products/JGPT/JGPTa/jgpt_status.sh

## Interpreting Results

- **Docker Services**: All 5 services (api, worker, web, db, redis) must be `[OK]`.
- **Ollama**: Must be listening on port 11434 and have `deepseek-coder` model.
- **API Health**: Must return `{"ok":true}`.
- **Authentication**: Admin login must succeed and protected route access must display `[OK]`.

If any step fails, the script will output details. Check `docker compose logs` for more info.
