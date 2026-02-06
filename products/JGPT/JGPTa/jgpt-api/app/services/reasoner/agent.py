import json
import re
import inspect
from typing import AsyncGenerator
from app.services.router import router
from app.services.reasoner.prompts import SYSTEM_PROMPT
from app.services.reasoner.tools import get_tool_descriptions, get_tool_names, get_tool_by_name

# Regex to parse the LLM output for Action/Action Input
ACTION_PATTERN = re.compile(r"Action:\s*(.+?)\nAction Input:\s*(.+)", re.DOTALL)

async def reasoner_agent(user_input: str, model: str = "llama3.2") -> AsyncGenerator[str, None]:
    """
    Executes the ReAct loop: Thought -> Action -> Observation -> Thought ...
    Yields Server-Sent Events (SSE) data strings.
    """
    
    tool_descriptions = get_tool_descriptions()
    tool_names = get_tool_names()
    
    # Initialize conversation history with system prompt
    current_prompt = SYSTEM_PROMPT.format(
        tool_descriptions=tool_descriptions,
        tool_names=tool_names,
        input=user_input
    )
    
    # We maintain a running log of the "scratchpad"
    scratchpad = ""
    
    max_steps = 5
    step_count = 0
    
    yield f"data: {json.dumps({'type': 'thought', 'content': 'Starting reasoning process...'})}\n\n"

    while step_count < max_steps:
        step_count += 1
        
        # 1. Call LLM
        # We append the scratchpad to the prompt to maintain state
        full_prompt = current_prompt + scratchpad
        
        # We might need to adjust this depending on how ollama_chat handles system/user separation
        # For simplicity, we'll treat it as a single prompt or handle it if ollama_chat expects list.
        # Looking at ollama_client.py (which I'm about to read/have read), it likely takes (model, system, prompt).
        # We'll pass the base instruction as system, and the running conversation as user prompt.
        
        # Actually, let's just pass the whole thing if the client supports it, or split it.
        # Let's assume standard usage:
        # Route the request through the centralized Model Router
        # We default to prefer_local=True for reasoning tasks
        response_text = await router.route_request(
            system_prompt="You are a reasoning agent. Follow the trace exactly.",
            user_prompt=full_prompt,
            task_type="reasoning",
            prefer_local=True
        )
        
        # Parse the output
        # Usually the model outputs "Thought: ... Action: ... Action Input: ..."
        # Or "Thought: ... Final Answer: ..."
        
        # We append the model's output to scratchpad
        scratchpad += response_text + "\n"
        
        # Check for Final Answer
        if "Final Answer:" in response_text:
            answer = response_text.split("Final Answer:", 1)[1].strip()
            yield f"data: {json.dumps({'type': 'answer', 'content': answer})}\n\n"
            data = {"type": "done"}
            yield f"data: {json.dumps(data)}\n\n"
            return

        # Check for Action
        # We look for the LAST "Action:" pattern in the response (or the first one if it generated one step)
        match = ACTION_PATTERN.search(response_text)
        
        if match:
            action_name = match.group(1).strip()
            action_input = match.group(2).strip()
            
            thought_content = response_text.split("Action:")[0].replace("Thought:", "").strip()
            yield f"data: {json.dumps({'type': 'thought', 'content': f'Thinking: {thought_content}'})}\n\n"
            yield f"data: {json.dumps({'type': 'tool_call', 'tool': action_name, 'input': action_input})}\n\n"

            # Execute Tool
            tool = get_tool_by_name(action_name)
            observation = ""
            if tool:
                try:
                    # Run the tool (assuming synchronous for now as per tools.py)
                    # If tool is async, we'd await it. Our python_repl is sync.
                    if inspect.iscoroutine(tool_result):
                        tool_result = await tool_result
                    observation = f"Observation: {tool_result}"
                except Exception as e:
                    observation = f"Observation: Error executing tool: {e}"
            else:
                observation = f"Observation: Tool '{action_name}' not found. Available tools: {tool_names}"
            
            yield f"data: {json.dumps({'type': 'tool_result', 'result': observation})}\n\n"

            # Append Observation to scratchpad so the model sees it in next turn
            scratchpad += observation + "\n"
            
        else:
            # If no action and no final answer, the model might be just thinking or failed format.
            # We treat it as a thought and continue, or stop if it seems stuck.
            yield f"data: {json.dumps({'type': 'thought', 'content': response_text})}\n\n"
            # If it didn't output an action, we might need to prompt it to continue? 
            # Or usually the scratchpad update is enough if we loop.
            # But if it stopped without Action or Final Answer, we force it to continue in next loop?
            # Actually, if it didn't produce an action, we should probably prompt "Action:" or similar?
            # For now, let's assume it outputted a Thought but forgot Action, or is verbose.
            pass
            
    yield f"data: {json.dumps({'type': 'error', 'content': 'Max reasoning steps reached.'})}\n\n"
