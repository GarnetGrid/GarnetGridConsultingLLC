
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class VizService:
    @staticmethod
    def generate_chart(data: List[Dict[str, Any]], chart_type: str, x_col: str, y_col: str, title: str = "Chart") -> str:
        """
        Generates a chart from a list of dictionaries and returns a base64 encoded string of the image.
        
        :param data: List of dicts, e.g. [{"category": "A", "val": 10}, ...]
        :param chart_type: "bar", "line", "scatter", "pie"
        :param x_col: Key for X-axis
        :param y_col: Key for Y-axis (or values for pie)
        :param title: Chart title
        :return: Base64 string of the PNG image
        """
        try:
            plt.figure(figsize=(10, 6))
            sns.set_theme(style="whitegrid")
            
            x_vals = [d.get(x_col) for d in data]
            y_vals = [d.get(y_col) for d in data]

            if chart_type == "bar":
                sns.barplot(x=x_vals, y=y_vals)
            elif chart_type == "line":
                sns.lineplot(x=x_vals, y=y_vals, marker='o')
            elif chart_type == "scatter":
                sns.scatterplot(x=x_vals, y=y_vals)
            elif chart_type == "pie":
                plt.pie(y_vals, labels=x_vals, autopct='%1.1f%%')
            else:
                return f"Error: Unsupported chart type '{chart_type}'"

            plt.title(title)
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return img_str
            
        except Exception as e:
            logger.error(f"Failed to generate chart: {e}")
            return f"Error generation chart: {str(e)}"
