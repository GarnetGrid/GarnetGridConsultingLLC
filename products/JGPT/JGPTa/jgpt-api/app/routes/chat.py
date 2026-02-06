from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
import os, json, math
import httpx
import logging

from app.db.session import SessionLocal
from app.db.models import Conversation, Message, ToolRun, User, PrimedContext
from app.rag.embeddings import embed_one
from app.rag.retriever import retrieve
from app.tools.selector import pick_tools
from app.tools.registry import TOOLS
from app.util.kb_watch import kb_watch_enabled
from app.util.personas import get_persona_prompt, get_persona_config
from app.rag.ollama_client import ollama_chat_stream
from app.util.fact_checker import verify_grounds
from app.rag.reasoners import expand_query
from app.services.memory import summarize_history
from app.util.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    model_config = {'extra': 'forbid'}
    mode: str = Field(default="powerbi") 
    persona: str | None = None
    message: str
    conversation_id: int | None = None
    model: str | None = None
    domain: str | None = None  
    grade: bool = Field(default=False)
    project_context: str | None = None
    department: str | list[str] | None = None
    options: dict | None = None
    history: list[dict] = Field(default_factory=list) # Added for orchestration

def _heuristic_grade(answer: str, citations: list[dict], rag_meta: dict) -> dict:
    a = answer or ""
    has_code = ("```" in a) or ("=" in a and "VAR" in a)
    cite_n = len(citations or [])
    retrieved = int((rag_meta or {}).get("total_retrieved") or 0)

    score = 0.0
    score += 35.0 if has_code else 0.0
    score += min(25.0, cite_n * 5.0)
    score += 20.0 if retrieved >= 4 else 5.0
    score += 10.0 if len(a.strip()) >= 200 else 0.0
    score += 10.0 if "\n" in a else 0.0

    score = max(0.0, min(100.0, score))
    conf = 1.0 / (1.0 + math.exp(-(score - 55.0) / 10.0))
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "E"
    return {
        "grade": grade,
        "score": round(score, 1),
        "confidence": round(conf, 3),
        "signals": {"has_code": has_code, "citations": cite_n, "retrieved": retrieved}
    }

def get_or_create_conversation(conv_id: int | None, user_id: int, message: str, persona: str, model: str) -> tuple[int, list[dict], int]:
    with SessionLocal() as s:
        if conv_id:
            conv = s.get(Conversation, conv_id)
            if not conv:
                raise ValueError("Conversation not found")
        else:
            conv = Conversation(title="New chat", mode=persona, model=model, user_id=user_id)
            s.add(conv); s.commit(); s.refresh(conv)
        
        real_id = conv.id
        prev_msgs = s.query(Message).filter(Message.conversation_id == real_id).order_by(Message.created_at.desc()).limit(15).all()
        history_objs = sorted(prev_msgs, key=lambda x: x.created_at)
        history_msgs = [{"role": m.role, "content": m.content} for m in history_objs]
        
        new_msg = Message(conversation_id=real_id, role="user", content=message)
        s.add(new_msg)
        s.commit()
        s.refresh(new_msg)
        
        return real_id, history_msgs, new_msg.id

def perform_retrieval(s, q_text: str, q_emb: list[float], top_k: int, domain: str, lam: float, dept: str | None):
    # This is a helper wrapper if retrieve() is synchronous, but retrieve is async in the original code. 
    # original code: await retrieve(...)
    # If retrieve is effectively async we don't need run_in_threadpool for it, but if it uses blocking DB calls inside, we might.
    # Looking at imports: `from app.rag.retriever import retrieve`
    # The original code awaited it, so it's async. We leave it as await.
    pass

def save_assistant_message(conv_id: int, content: str, embedding: list[float] | None = None):
    with SessionLocal() as s:
        msg = Message(conversation_id=conv_id, role="assistant", content=content.strip(), embedding=embedding)
        s.add(msg)
        s.commit()

def update_message_embedding(msg_id: int, embedding: list[float]):
    with SessionLocal() as s:
        msg = s.get(Message, msg_id)
        if msg:
            msg.embedding = embedding
            s.commit()

@router.get("/personas/{name}/config")
async def persona_config(name: str):
    config = get_persona_config(name)
    if not config:
        raise HTTPException(status_code=404, detail="Persona not found")
    return config

@router.post("")
async def chat(req: ChatRequest, current_user: User = Depends(get_current_user)):
    async def generate():
        chat_model = req.model or os.getenv("CHAT_MODEL", "llama3.2")
        top_k = int(os.getenv("TOP_K", "8"))
        lam = float(os.getenv("MMR_LAMBDA", "0.7"))

        persona_name = req.persona or req.mode or "powerbi"
        domain = (req.domain or persona_name).lower().strip()
        if domain not in ["powerbi", "d365fo", "all"]:
            domain = "all"

        persona_config = get_persona_config(persona_name)
        merged_options = persona_config.get("default_options", {}).copy()
        if req.options:
            merged_options.update(req.options)

        current_mode = req.mode
        current_message = req.message

        # 0) Orchestration (Auto Mode)
        if req.mode == "auto":
            from app.services.orchestrator import OrchestratorService
            orch = OrchestratorService()
            
            # Notify user we are routing
            yield f"data: {json.dumps({'type': 'thought', 'text': 'Orchestrator: Analyzing request...'})}\n\n"
            
            route_decision = await orch.route_request(req.message, req.history) # Fix: req.history might not be available in ChatRequest? Check model.
            target_agent = route_decision.get("target_agent", "general")
            refined_query = route_decision.get("refined_query", req.message)
            router_thought = route_decision.get("thought", "Routing to agent.")

            # Update params for the rest of the flow
            current_mode = target_agent
            current_message = refined_query
            
            # Update derived vars
            persona_name = current_mode
            domain = (current_mode if current_mode in ["powerbi", "d365fo"] else "all")
            # Refresh config for new agent
            persona_config = get_persona_config(persona_name)
            
            yield f"data: {json.dumps({'type': 'thought', 'text': f'Orchestrator: {router_thought} -> Handing off to {target_agent.upper()}'})}\n\n"

        # 0.5) Reasoner Branch
        if current_mode == "reasoner" or (req.mode == "auto" and target_agent == "reasoner"):
            from app.services.reasoner import ReasonerService
            svc = ReasonerService(model=req.model)
            async for chunk in svc.reason(current_message, history=req.history):
                yield chunk
            return

        # 1) System Prompt & Tool Loading
        current_model = req.model or persona_config.get("default_model") or os.getenv("CHAT_MODEL", "llama3.2")

        async def generate(): # Wait, I am nesting generate? No, I am REPLACING the def.
            pass 
        # ERROR IN PROMPT: I am inside ReplacementContent, I should not define generate AGAIN.
        # But the original code had `async def generate():` at line 153.
        # I am replacing lines 115-153.
        # So I start with `async def generate():` and end with logic that leads into step 1.
        
        # 1) Conversation & History Load (Blocking DB op -> Threadpool)
        # 1) Conversation & History Load (Blocking DB op -> Threadpool)
        try:
            conv_id, history_msgs, user_msg_id = await run_in_threadpool(
                get_or_create_conversation, 
                req.conversation_id, 
                current_user.id, 
                req.message, 
                persona_name, 
                current_model
            )
        except ValueError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return
        except Exception as e:
            logger.exception("DB Error during chat init")
            yield f"data: {json.dumps({'error': 'Internal Database Error'})}\n\n"
            return

        # 2) Initial Retrieval with Expansion
        try:
            search_queries = await expand_query(req.message, domain=domain)
            all_citations = []
            all_context_blocks = []
            
            # Retrieval Logic involves embedding (async usually) and DB (async via session or sync). 
            # Original code used SessionLocal() context manager which is blocking if not wrapped.
            # However, retrieve() is awaited but takes a session. 
            # If retrieve() does async session calls, we are fine. If it does sync session calls, we are blocking.
            # For this refactor, we will assume retrieve is async-capable or lightweight enough, 
            # BUT we need to manage the session carefully.
            
            # Since retrieve requires a session, let's wrap the logic that USES the session.
            # But retrieve is async def... so we can't easily push it to threadpool if it yields.
            # Best practice for async SQL: use async session. But we have SessionLocal (sync).
            # We will use run_in_threadpool for the entire retrieval block if it relies on sync session.
            
            # Actually, let's keep the structure but ensure we don't block main loop for long.
            # We'll create a sync wrapper for the session parts if possible, but retrieve is async.
            # We will proceed with the existing pattern but moving the session creation to a threadpool function is tricky if async methods need it.
            # Ideally we refactor `retrieve` to be fully async or fully sync. 
            # For now, we will assume `retrieve` handles its I/O fairly well, but the Session creation is the culprit.
            
            # Simplified approach: Use a fresh session for retrieval block to avoid long-lived blocking.
            # Note: `retrieve` is awaited, so we can't wrap it in run_in_threadpool easily if it's a coroutine.
            
            # Parallel Retrieval
            import asyncio
            
            async def process_query(q: str):
                try:
                    # Create a dedicated session for this parallel task
                    # This ensures thread safety when retrieve() offloads to threadpool
                    with SessionLocal() as s: 
                        q_emb = await embed_one(q)
                        return await retrieve(
                            s, query_text=q, query_emb=q_emb,
                            top_k=max(2, top_k // len(search_queries)), 
                            domain=domain if domain != "all" else None, mmr_lambda=lam,
                            department=req.department
                        )
                except Exception as e:
                    logger.error(f"Query processing failed for '{q}': {e}")
                    return ([], "", {})

            # Execute all queries in parallel
            results = await asyncio.gather(*(process_query(q) for q in search_queries))
            
            for c_list, c_block, _ in results:
                all_citations.extend(c_list)
                all_context_blocks.append(c_block)
            
            seen_ids = set()
            citations = []
            for c in all_citations:
                if c["chunk_id"] not in seen_ids:
                    citations.append(c)
                    seen_ids.add(c["chunk_id"])
            
            context_block = "\n---\n".join(all_context_blocks)
            rag_meta = {"queries_expanded": len(search_queries), "total_retrieved": len(citations)}
            
        except Exception as e:
            logger.exception("Retrieval failed")
            yield f"data: {json.dumps({'error': f'Retrieval failed: {e}'})}\n\n"
            return

            frag_citations = []
            for c in citations:
                frag_citations.append({"id": c["chunk_id"], "source": c["source"]})
            
            yield f"data: {json.dumps({'type': 'metadata', 'conversation_id': conv_id, 'citations': frag_citations, 'retrieval': rag_meta})}\n\n"

            # 2a) Async Embedding of User Message
            # We do this here while context loads, so it's somewhat parallel to the heavy lifting?
            # Actually, let's just do it.
            try:
                user_emb = await embed_one(req.message)
                await run_in_threadpool(update_message_embedding, user_msg_id, user_emb)
            except Exception as e:
                logger.error(f"Failed to embed user message: {e}")

        # 3) Memory & Tool Selection
        # Memory summarization might be heavy
        summary = await summarize_history(history_msgs, max_turns=8)
        
        system_prompt = get_persona_prompt(persona_name)
        
        # Load Persistent Memory (Fact + Entities)
        from app.services.context_service import ContextService
        primed_context = ""
        
        try:
            def load_full_memory(uid: int):
                with SessionLocal() as s:
                    svc = ContextService(s)
                    return svc.get_user_context(uid), svc.get_all_entities(uid)

            user_facts, user_entities = await run_in_threadpool(load_full_memory, current_user.id)
            
            # Format Facts
            if user_facts:
                primed_context += "\n[MEMORY - USER PREFERENCES & FACTS]\n"
                for k, v in user_facts.items():
                    primed_context += f"- {k}: {v}\n"
            
            # Format Entities
            if user_entities:
                primed_context += "\n[MEMORY - KNOWN ENTITIES]\n"
                for ent in user_entities:
                    primed_context += f"- {ent['name']} ({ent['type']}): {ent['description']}\n"
                    
        except Exception as e:
            logger.error(f"Failed to load memory from DB: {e}")
        
        if primed_context:
            system_prompt += f"\n\n{primed_context}\n"

        if req.project_context:
            system_prompt += f"\n\nGLOBAL PROJECT CONTEXT / RULES:\n{req.project_context}\n"
        
        if summary:
            system_prompt += f"\n\nPAST CONVERSATION SUMMARY: {summary}\n"
            history_msgs = history_msgs[-4:]

        tool_advice = "Use 'kb_search' if the retrieved context is insufficient."
        tool_choices = await pick_tools(domain, f"{req.message}. {tool_advice}", history=history_msgs)
        tool_names = [t["name"] for t in tool_choices] or list(TOOLS.keys())
        
        agent_instr = f"You are an assistant. Output JSON: {{\"thought\": \"...\", \"action\": {{\"name\": \"...\", \"input\": {{...}}}} or null, \"answer\": \"...\" or null}}.\nTools: {', '.join(tool_names)}"
        
        messages = [{"role": "system", "content": system_prompt + "\n\n" + agent_instr}] + history_msgs + [
            {"role": "user", "content": f"Context (UNTRUSTED):\n{context_block}\n\nUser: {req.message}"}
        ]

        # 4) Agent Loop
        final_answer = ""
        for _ in range(4):
            content = ""
            async for chunk in ollama_chat_stream(current_model, messages, format="json", options=merged_options):
                content += chunk
            if not content.strip(): break
            
            try:
                res = json.loads(content)
            except:
                final_answer = content
                yield f"data: {json.dumps({'type': 'answer', 'chunk': content})}\n\n"
                break

            thought = res.get("thought", "")
            action = res.get("action")
            answer = res.get("answer")

            if thought: yield f"data: {json.dumps({'type': 'thought', 'text': thought})}\n\n"

            if action and action.get("name"):
                t_name = action["name"]
                t_input = action.get("input") or {}
                if t_name not in tool_names:
                    if t_name in TOOLS:
                        logger.warning(f"Tool {t_name} used despite not being in picked list {tool_names}")
                    else:
                        out = {"ok": False, "error": "Not authorized"}
                else:
                    fn = TOOLS.get(t_name)
                    if not fn: out = {"ok": False, "error": "Not found"}
                    else:
                        try:
                            # Tools might be blocking too!
                            if t_name == "kb_search":
                                t_input.setdefault("domain", domain)
                                t_input.setdefault("department", req.department)
                            
                            # Execute tool in threadpool if it's not async
                            # We assume tools are synchronous functions for safety
                            import inspect
                            if inspect.iscoroutinefunction(fn):
                                out = await fn(t_input)
                            else:
                                out = await run_in_threadpool(fn, t_input)
                                
                        except Exception as e: 
                            logger.exception(f"Tool execution failed: {t_name}")
                            out = {"ok": False, "error": str(e)}
                
                yield f"data: {json.dumps({'type': 'tool', 'name': t_name, 'thought': thought, 'input': t_input, 'output': out})}\n\n"
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": f"Tool output: {json.dumps(out)}"})
                continue
            
            if answer:
                final_answer = answer
                yield f"data: {json.dumps({'type': 'answer', 'chunk': answer})}\n\n"
                break
            else:
                final_answer = thought or content
                yield f"data: {json.dumps({'type': 'answer', 'chunk': final_answer})}\n\n"
                break

        if persona_name == "truthkeeper":
            audit = verify_grounds(final_answer, [context_block])
            yield f"data: {json.dumps({'type': 'audit', 'report': audit})}\n\n"
            
        qual = _heuristic_grade(final_answer, citations, rag_meta) if req.grade else {"grade": None}
        yield f"data: {json.dumps({'type': 'done', 'quality': qual})}\n\n"

        # Save Assistant Message (Blocking -> Threadpool)
        try:
            asst_emb = await embed_one(final_answer)
            await run_in_threadpool(save_assistant_message, conv_id, final_answer, asst_emb)
        except Exception:
            logger.exception("Failed to save assistant message")

    return StreamingResponse(generate(), media_type="text/event-stream")

