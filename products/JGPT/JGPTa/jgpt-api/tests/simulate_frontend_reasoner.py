import asyncio
import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure the app working directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- MOCK DEPENDENCIES BEFORE IMPORTING APP MODULES ---
# This is necessary because data science libs might be missing in the env,
# and we don't need them for this connectivity test.
mock_lib = MagicMock()
sys.modules["matplotlib"] = mock_lib
sys.modules["matplotlib.pyplot"] = mock_lib
sys.modules["pandas"] = mock_lib
sys.modules["seaborn"] = mock_lib
sys.modules["sklearn"] = mock_lib
sys.modules["plotly"] = mock_lib
sys.modules["plotly.express"] = mock_lib

from app.routes.chat import chat, ChatRequest
from app.db.models import User

async def main():
    print("--- Starting Reasoner Simulation ---")

    # Mock User
    mock_user = User(id=1, email="test@test.com", is_active=True)

    # Patch the ReasonerService where it is imported in app.routes.chat
    # Note: 'app.routes.chat' imports it inside the function, 
    # so we might need to patch 'app.services.reasoner.ReasonerService' globally
    with patch("app.services.reasoner.ReasonerService") as MockReasonerService:
        mock_instance = MockReasonerService.return_value
        
        # Define what the reason method yields
        async def mock_reason_generator(message, history=None):
            yield f"data: {json.dumps({'type': 'thought', 'text': 'Reasoner: Thinking...'})}\\n\\n"
            await asyncio.sleep(0.01)
            yield f"data: {json.dumps({'type': 'thought', 'text': 'Reasoner: Executing tool...'})}\\n\\n"
            await asyncio.sleep(0.01)
            yield f"data: {json.dumps({'answer': '42'})}\\n\\n"

        mock_instance.reason.side_effect = mock_reason_generator

        # Create request
        req = ChatRequest(
            message="What is the meaning of life?",
            mode="reasoner",
            history=[]
        )

        try:
            # Call the endpoint function directly
            print("Invoking chat()...")
            response = await chat(req, current_user=mock_user)
            
            # The response is a StreamingResponse
            print("Consuming stream...")
            thought_count = 0
            
            async for chunk in response.body_iterator:
                # Chunk might be bytes or str, FastAPI StreamingResponse usually handles bytes
                # But our generator yields strings. StreamingResponse might rely on encoding.
                # In unit tests with starlette/fastapi, usually we get bytes.
                text_chunk = chunk
                if isinstance(chunk, bytes):
                    text_chunk = chunk.decode("utf-8")
                
                print(f"Received Chunk: {text_chunk.strip()}")
                
                if '"type": "thought"' in text_chunk:
                    thought_count += 1
            
            if thought_count >= 2:
                print(f"\nSUCCESS: Received {thought_count} thought events.")
            else:
                print(f"\nFAILURE: Expected at least 2 thought events, got {thought_count}.")
                sys.exit(1)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
