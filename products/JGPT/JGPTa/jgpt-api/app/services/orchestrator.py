import json
import os
import httpx

class OrchestratorService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        self.model = os.getenv("CHAT_MODEL", "llama3.2")
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        try:
            with open("app/copilots/orchestrator/system_prompt.md", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "You are an Orchestrator. Route to: analyst, powerbi, d365fo, or general."

    async def route_request(self, user_message: str, history: list) -> dict:
        """
        Analyzes the user message and history to determine the best agent.
        Returns: {"target_agent": str, "thought": str, "refined_query": str}
        """
        
        # Prepare context for the Orchestrator
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"History: {json.dumps(history[-2:])}\n\nCurrent Request: {user_message}"}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.1} # Low temp for deterministic routing
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data.get("message", {}).get("content", "")
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Fallback if valid JSON isn't returned
                    print(f"Orchestrator JSON Error. Raw: {content}")
                    return {"target_agent": "general", "thought": "Failed to parse JSON, defaulting to general.", "refined_query": user_message}
            
            except Exception as e:
                print(f"Orchestrator API Error: {e}")
                return {"target_agent": "general", "thought": f"Error calling LLM: {e}", "refined_query": user_message}
