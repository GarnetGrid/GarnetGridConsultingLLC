import re

def verify_grounds(answer: str, context_blocks: list[str]) -> dict:
    """
    Heuristic check for potential hallucinations.
    In a real system, this would call another LLM (Judge) to verify each claim.
    """
    a_lower = answer.lower()
    missing_terms = []
    
    # Simple check for keywords in answer that are NOT in context
    # Focusing on technical tokens (all caps or camelCase or with underscores)
    tokens = set(re.findall(r'\b[A-Za-z_]{4,}\b', answer))
    context_text = " ".join(context_blocks).lower()
    
    for t in tokens:
        # Ignore common words
        if t.lower() in ["answer", "question", "context", "provide", "based", "below", "citation", "source"]:
            continue
        if t.lower() not in context_text:
            # Check if it might be a technical token
            if any(c.isupper() for c in t) or "_" in t:
                missing_terms.append(t)
                
    conf = 100
    if missing_terms:
        conf = max(10, 100 - (len(missing_terms) * 15))
        
    grade = "High" if conf > 80 else "Medium" if conf > 50 else "Low"
    
    return {
        "score": conf,
        "grade": grade,
        "missing_references": missing_terms[:5],
        "audit_id": "FACT-JGPT-001"
    }
