from __future__ import annotations
import json
import os
import asyncio
from app.rag.ollama_client import ollama_chat
from app.tools.registry import TOOLS
from app.tools.selector import pick_tools

class ReasonerService:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("CHAT_MODEL", "llama3.2")
    
    async def decompose(self, query: str) -> list[str]:
        """Breaks a complex query into sub-questions."""
        system = (
            "You are a Senior Business Analyst. Your goal is to break down a complex user request "
            "into 2-4 independent, atomic sub-questions that can be answered by data tools (SQL, Search, Analytics). "
            "Return STRICT JSON: {\"steps\": [\"sub-question 1\", \"sub-question 2\"]}"
        )
        try:
            content = await ollama_chat(self.model, system, f"Request: {query}")
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content:
                content = content[content.find("{"):content.rfind("}")+1]
            
            data = json.loads(content)
            return data.get("steps", [query])
        except Exception as e:
            print(f"Decomposition failed: {e}")
            return [query]

    async def execute_step(self, step: str, context: str = "") -> str:
        """Solves a single sub-question using tools."""
        # 1. Pick Tool
        # We assume pick_tools returns a list of tool metadata dicts
        tools = await pick_tools("all", step)
        tool_names = [t["name"] for t in tools]
        
        # Fallback if no specific tools picked, give a broad set or just specific relevant ones?
        # For now, let's trust the picker. If empty, maybe default to web_search if available?
        if not tool_names and "web_search" in TOOLS:
            tool_names = ["web_search"]

        system = (
            f"You are an executor agent. Solve the sub-question: '{step}'. "
            f"Available Tools: {json.dumps(tool_names)}. "
            f"Context: {context[:1000]}... "
            "Output JSON: {\"action\": {\"name\": \"tool_name\", \"input\": {...}} or null, \"answer\": \"...\"}"
        )
        
        try:
            content = await ollama_chat(self.model, system, f"Sub-question: {step}")
            
            # Use improved JSON extraction
            json_str = content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content:
                # heuristic to find the outer brace
                json_str = content[content.find("{"):content.rfind("}")+1]
            
            try:
                res = json.loads(json_str)
            except:
                # If parsing fails, treat the whole content as an answer/explanation
                return f"Analysis: {content}"
            
            action = res.get("action")
            if action and action.get("name") in TOOLS:
                t_name = action["name"]
                t_input = action.get("input", {})
                
                fn = TOOLS[t_name]
                try:
                    import inspect
                    if inspect.iscoroutinefunction(fn):
                        tool_res = await fn(t_input)
                    else:
                        # Run sync tools in threadpool to avoid blocking event loop
                        from fastapi.concurrency import run_in_threadpool
                        tool_res = await run_in_threadpool(fn, t_input)
                        
                    return f"Tool({t_name}) Output: {str(tool_res)}"
                except Exception as tool_err:
                    return f"Tool({t_name}) Failed: {str(tool_err)}"
            
            return res.get("answer", content)
            
        except Exception as e:
            return f"Error executing step '{step}': {e}"

    async def synthesize(self, query: str, results: list[str]) -> str:
        """Combines sub-answers into a final response."""
        system = "You are a synthesizer. specific constraints: combine the following findings into a cohesive answer to the user's original question."
        findings = "\n".join([f"- {r}" for r in results])
        prompt = f"Original Question: {query}\n\nFindings:\n{findings}"
        return await ollama_chat(self.model, system, prompt)

    async def reason(self, query: str, history: list[dict] = None) -> dict:
        """Main entry point."""
        yield f"data: {json.dumps({'type': 'thought', 'text': 'Reasoner: Decomposing query...'})}\n\n"
        steps = await self.decompose(query)
        yield f"data: {json.dumps({'type': 'thought', 'text': f'Reasoner: Identified {len(steps)} steps: {steps}'})}\n\n"
        
        results = []
        for step in steps:
            yield f"data: {json.dumps({'type': 'thought', 'text': f'Reasoner: Executing step: {step}'})}\n\n"
            res = await self.execute_step(step)
            results.append(res)
            yield f"data: {json.dumps({'type': 'thought', 'text': f'Reasoner: Result: {res[:100]}...'})}\n\n"
        
        yield f"data: {json.dumps({'type': 'thought', 'text': 'Reasoner: Synthesizing final answer...'})}\n\n"
        final_answer = await self.synthesize(query, results)
        
        yield f"data: {json.dumps({'type': 'answer', 'chunk': final_answer})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
