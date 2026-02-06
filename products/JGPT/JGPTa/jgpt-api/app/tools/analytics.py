from typing import Dict, Any, List
from app.services.viz_service import VizService

def run_generate_chart(inp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a statistical chart (bar, line, scatter, pie) from provided JSON data.
    Input format:
    {
      "chart_type": "bar",
      "data": [{"month": "Jan", "sales": 100}, {"month": "Feb", "sales": 120}],
      "x": "month",
      "y": "sales",
      "title": "Monthly Sales"
    }
    Returns: {"image_base64": "..."}
    """
    try:
        data = inp.get("data", [])
        chart_type = inp.get("chart_type", "bar")
        x_col = inp.get("x")
        y_col = inp.get("y")
        title = inp.get("title", "Chart")

        if not data or not x_col or not y_col:
            return {"error": "Missing 'data', 'x', or 'y' parameters."}

        # Return structured data for frontend rendering (Recharts)
        return {
            "status": "success", 
            "message": "Chart data generated.",
            "type": "chart_data",
            "chart_config": {
                "type": chart_type,
                "title": title,
                "x_key": x_col,
                "y_key": y_col,
                "data": data
            }
        }

    except Exception as e:
        return {"error": f"Tool execution failed: {e}"}
