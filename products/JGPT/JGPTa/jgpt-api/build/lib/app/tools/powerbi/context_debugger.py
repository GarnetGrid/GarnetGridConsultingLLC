from __future__ import annotations
from typing import Dict, Any

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    scenario = inp.get("scenario","card_vs_matrix")
    return {
        "tool": "powerbi.context_debugger",
        "scenario": scenario,
        "explanation": (
            "Cards evaluate a measure once under the current filter context. "
            "Matrices/tables evaluate the measure per cell (each row/col header adds filters). "
            "Totals are *recomputed*, not a sum of visible rows, unless you force it with SUMX over the grain."
        ),
        "patterns": [
            "Total-as-sum: SUMX(VALUES(Dim[Key]), [Measure])",
            "Context transition: CALCULATE converts row context to filter context (inside iterators, etc.)",
        ],
        "diagnostic_questions": [
            "What fields are on the matrix rows/columns?",
            "Does your measure use iterators (SUMX/AVERAGEX) or CALCULATE?"
        ]
    }
