from fastapi import APIRouter, UploadFile, File, HTTPException
from app.tools.powerbi import model_primer
import json

router = APIRouter()

@router.post("/prime")
async def prime_powerbi_model(file: UploadFile = File(...)):
    """
    Accepts a .bim json file and primes the user context with it.
    """
    if not file.filename.endswith(('.json', '.bim')):
        raise HTTPException(status_code=400, detail="File must be a .bim or .json file")

    content = await file.read()
    try:
        bim_data = json.loads(content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    # Mock user ID for now since auth might be loose in dev
    # Ideally this comes from a dependency injection
    result = model_primer.run({
        "model_name": file.filename,
        "bim_content": bim_data,
        "_user_id": "dev-user" 
    })
    
    if result.get("error"):
         raise HTTPException(status_code=500, detail=result["error"])

    return result
