from __future__ import annotations
from typing import Dict, Any

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    date_table = inp.get("date_table","'Date'")
    week_start_col = inp.get("week_start_col","WeekStartDate")
    sales_measure = inp.get("sales_measure","[Sales]")
    return {
        "tool": "powerbi.trailing_weeks_generator",
        "dax": f"""-- Assumes {date_table}[{week_start_col}] exists and is a date representing the week start
Sales W-1 =
VAR w0 = MAX({date_table}[{week_start_col}])
RETURN
CALCULATE(
  {sales_measure},
  FILTER(ALL({date_table}), {date_table}[{week_start_col}] = w0 - 7)
)

Sales W-2 =
VAR w0 = MAX({date_table}[{week_start_col}])
RETURN
CALCULATE(
  {sales_measure},
  FILTER(ALL({date_table}), {date_table}[{week_start_col}] = w0 - 14)
)

Sales W-3 =
VAR w0 = MAX({date_table}[{week_start_col}])
RETURN
CALCULATE(
  {sales_measure},
  FILTER(ALL({date_table}), {date_table}[{week_start_col}] = w0 - 21)
)
""",
        "notes": [
            "If you slice by YearWeek, you can anchor w0 using SELECTEDVALUE(YearWeek) then lookup its WeekStartDate.",
            "Use REMOVEFILTERS on non-date dimensions only if needed."
        ]
    }
