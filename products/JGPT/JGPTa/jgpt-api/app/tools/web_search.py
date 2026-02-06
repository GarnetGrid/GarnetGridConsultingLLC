import json

def web_search(inputs: dict) -> dict:
    """
    Search the web for a query.
    Inputs: {"query": str}
    """
    query = inputs.get("query", "").lower()
    
    # Demonstration mock results for common technical queries
    if "dax" in query or "power bi" in query:
        return {
            "results": [
                {"title": "DAX Guide - CALCULATE", "url": "https://dax.guide/calculate/", "snippet": "CALCULATE is the most important function in DAX. It evaluates an expression in a modified filter context."},
                {"title": "Microsoft Power BI Blog", "url": "https://powerbi.microsoft.com/blog/", "snippet": "Latest updates on Power BI features, including the new AI-powered report creator."}
            ],
            "source": "Mock search engine"
        }
    
    if "d365" in query or "f&o" in query:
        return {
            "results": [
                {"title": "D365 F&O Documentation", "url": "https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/", "snippet": "Core financial and operational capabilities of Dynamics 365 Finance and Operations."},
                {"title": "X++ Language Reference", "url": "https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-language-reference", "snippet": "X++ is an object-oriented, strongly typed programming language used in D365 F&O."}
            ],
            "source": "Mock search engine"
        }

    return {
        "results": [
            {"title": f"Search results for {query}", "url": "https://example.com/search", "snippet": "Generic search results demonstrating the agent's ability to query the external web."}
        ],
        "source": "Mock search engine"
    }
