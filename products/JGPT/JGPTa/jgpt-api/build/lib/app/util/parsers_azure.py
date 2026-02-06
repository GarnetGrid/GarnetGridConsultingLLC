
import os
import requests
from pathlib import Path
from typing import Tuple, Optional

# Constants
ENDPOINT_ENV = "AZURE_FORM_RECOGNIZER_ENDPOINT"
KEY_ENV = "AZURE_FORM_RECOGNIZER_KEY"

def is_azure_configured() -> bool:
    return bool(os.getenv(ENDPOINT_ENV) and os.getenv(KEY_ENV))

def parse_pdf_azure(path: Path) -> Tuple[str, str]:
    """
    Submits PDF to Azure Document Intelligence for Layout Analysis.
    Returns (markdown_content, mime_type).
    """
    endpoint = os.getenv(ENDPOINT_ENV).rstrip("/")
    key = os.getenv(KEY_ENV)
    
    if not endpoint or not key:
        raise ValueError("Azure credentials missing")

    # API Version (2023-07-31 supports markdown output)
    api_url = f"{endpoint}/formrecognizer/documentModels/prebuilt-layout:analyze?api-version=2023-07-31&outputContentFormat=markdown"
    
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/pdf"
    }

    # 1. Submit Job
    with open(path, "rb") as f:
        data = f.read()
        
    resp = requests.post(api_url, headers=headers, data=data)
    resp.raise_for_status()
    
    # 2. Poll for Result
    operation_url = resp.headers["Operation-Location"]
    import time
    
    for _ in range(60): # logical timeout
        poll_resp = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": key})
        poll_resp.raise_for_status()
        status = poll_resp.json().get("status")
        
        if status == "succeeded":
            result = poll_resp.json()
            content = result["analyzeResult"]["content"]
            return content, "application/pdf"
        
        if status == "failed":
            raise RuntimeError(f"Azure Analysis Failed: {poll_resp.text}")
            
        time.sleep(1)
        
    raise TimeoutError("Azure Analysis timed out")
