import os
import json
from pathlib import Path

COPILOTS_DIR = Path(__file__).parent.parent / "copilots"

def get_available_personas():
    """Returns a list of available persona names (folder names)."""
    if not COPILOTS_DIR.exists():
        return []
    return [d.name for d in COPILOTS_DIR.iterdir() if d.is_dir()]

def load_persona_prompt(name: str):
    """Loads the system_prompt.md for a given persona."""
    path = COPILOTS_DIR / name / "system_prompt.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None

def get_persona_config(name: str) -> dict:
    """Loads the config.json for a given persona."""
    path = COPILOTS_DIR / name / "config.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error loading config for {name}: {e}")
    return {}

def get_persona_prompt(name: str):
    """Returns the persona prompt or a default if not found."""
    prompt = load_persona_prompt(name)
    if prompt:
        return prompt
    
    # Minimal default if none found
    return "You are JGPT, a helpful technical AI assistant."
