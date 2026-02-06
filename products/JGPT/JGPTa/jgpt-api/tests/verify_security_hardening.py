import sys
import os
import pytest
from pydantic import ValidationError

# Ensure path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock
sys.modules["matplotlib"] = MagicMock()
sys.modules["matplotlib.pyplot"] = MagicMock()
sys.modules["seaborn"] = MagicMock()

from app.routes.chat import ChatRequest
from app.routes.auth_routes import UserCreate, ApiKeyCreate
from app.routes.admin import SystemSettings

def test_chat_request_forbid_extra():
    print("Testing ChatRequest...")
    try:
        ChatRequest(message="hello", malicious_field="payload")
        print("FAILED: ChatRequest accepted extra field")
        sys.exit(1)
    except ValidationError:
        print("SUCCESS: ChatRequest rejected extra field")

def test_user_create_forbid_extra():
    print("Testing UserCreate...")
    try:
        UserCreate(email="test@example.com", password="password", is_admin=True)
        print("FAILED: UserCreate accepted extra field")
        sys.exit(1)
    except ValidationError:
        print("SUCCESS: UserCreate rejected extra field")

def test_api_key_create_forbid_extra():
    print("Testing ApiKeyCreate...")
    try:
        ApiKeyCreate(name="test-key", malicious="data")
        print("FAILED: ApiKeyCreate accepted extra field")
        sys.exit(1)
    except ValidationError:
        print("SUCCESS: ApiKeyCreate rejected extra field")

def test_system_settings_forbid_extra():
    print("Testing SystemSettings...")
    try:
        SystemSettings(chunk_size=500, malicious_config="overwrite")
        print("FAILED: SystemSettings accepted extra field")
        sys.exit(1)
    except ValidationError:
        print("SUCCESS: SystemSettings rejected extra field")

if __name__ == "__main__":
    test_chat_request_forbid_extra()
    test_user_create_forbid_extra()
    test_api_key_create_forbid_extra()
    test_system_settings_forbid_extra()
