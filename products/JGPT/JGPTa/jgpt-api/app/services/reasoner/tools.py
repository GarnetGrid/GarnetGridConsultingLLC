import sys
import io
import contextlib

class Tool:
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    def run(self, input_str):
        return self.func(input_str)

def python_repl(code: str) -> str:
    """
    Executes Python code in a sandboxed environment and returns the output (stdout).
    Use this for math, string manipulation, or data analysis.
    """
    # Remove markdown code blocks if present
    code = code.replace("```python", "").replace("```", "").strip()
    
    # Redirect stdout to capture print statements
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    
    # Safe(r) globals - restrict access to dangerous modules if possible
    # For now, we allow standard execution but in a production env we would sandbox this further.
    execution_globals = {
        "math": __import__("math"),
        "datetime": __import__("datetime"),
        "random": __import__("random"),
        "print": print
    }
    
    try:
        exec(code, execution_globals)
        output = redirected_output.getvalue()
        if not output:
             return "(Code executed with no output. Did you forget to print?)"
        return output
    except Exception as e:
        return f"Error executing code: {e}"
    finally:
        sys.stdout = old_stdout

# Define the available tools
async def context_retriever(query: str) -> str:
    """
    Retrieves relevant context from the JGPT Knowledge Base.
    Use this to find information about the user's organization, documents, or previous knowledge.
    """
    try:
        # Lazy imports to avoid circular dependencies
        from app.db.session import SessionLocal
        from app.rag.ollama_client import ollama_embed
        from app.rag.retriever import retrieve

        session = SessionLocal()
        try:
             # Embedding
             query_emb = await ollama_embed(model="llama3.2", text=query)
             
             # Retrieve (top_k=3 to keep context concise)
             citations, context_str, meta = await retrieve(
                 session=session,
                 query_text=query,
                 query_emb=query_emb,
                 top_k=3,
                 domain=None,
                 mmr_lambda=0.7 # High diversity
             )
             
             if not context_str:
                 return "No relevant context found in the Knowledge Base."
             
             return f"Retrieved Context:\n{context_str}"

        except Exception as e:
            return f"Error retrieving context: {e}"
        finally:
            session.close()

# Define the available tools
TOOLS = [
    Tool(
        name="PythonREPL",
        description="A Python shell. Use this to execute python commands. Input should be a valid python script. IMPORTANT: You must PRINT your results to see them.",
        func=python_repl
    ),
    Tool(
        name="ContextRetriever",
        description="Search the Knowledge Base for documents. Input: a simple search query string.",
        func=context_retriever
    )
]

def get_tool_descriptions():
    return "\n".join([f"{t.name}: {t.description}" for t in TOOLS])

def get_tool_names():
    return ", ".join([t.name for t in TOOLS])

def get_tool_by_name(name):
    for tool in TOOLS:
        if tool.name == name:
            return tool
    return None
