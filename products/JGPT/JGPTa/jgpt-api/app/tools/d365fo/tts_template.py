from __future__ import annotations
from typing import Dict, Any

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "tool":"d365fo.tts_template",
        "xpp": """try
{
    ttsBegin;

    // TODO: your writes here

    ttsCommit;
}
catch (Exception::Error)
{
    ttsAbort;
    throw;
}
""",
        "notes":[
            "ttsBegin increments ttsLevel; commit happens when it returns to 0.",
            "If an exception occurs before the final commit, you must ttsAbort (or allow unwind) and rethrow."
        ]
    }
