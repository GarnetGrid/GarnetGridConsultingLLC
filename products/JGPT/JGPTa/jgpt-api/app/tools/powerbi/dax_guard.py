from __future__ import annotations
import re

BANNED_IN_MEASURES = [
    ("EARLIER", "Avoid EARLIER/EARLIEST in measures; use variables + SELECTEDVALUE/ISINSCOPE or a calculated column."),
    ("EARLIEST", "Avoid EARLIER/EARLIEST in measures; use variables + SELECTEDVALUE/ISINSCOPE or a calculated column."),
]

def _extract_dax_blocks(text: str) -> list[str]:
    blocks = []
    for m in re.finditer(r"```\s*dax\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL):
        blocks.append(m.group(1).strip())
    return blocks

def run(payload: dict) -> dict:
    """Best-practice guard for generated DAX."""
    text = (payload or {}).get("text","") or ""
    blocks = _extract_dax_blocks(text)
    issues = []
    for idx, dax in enumerate(blocks, start=1):
        upper = dax.upper()
        for token, msg in BANNED_IN_MEASURES:
            if token in upper:
                issues.append({"block": idx, "token": token, "message": msg})
        # Common conceptual red flags we can detect syntactically:
        if "EARLIER(" in upper and "CALCULATE(" in upper:
            issues.append({"block": idx, "token": "EARLIER+CALCULATE", "message": "EARLIER with CALCULATE usually indicates a calculated-column pattern mistakenly placed in a measure."})
    return {"tool":"powerbi.dax_guard","block_count": len(blocks), "issue_count": len(issues), "issues": issues}
