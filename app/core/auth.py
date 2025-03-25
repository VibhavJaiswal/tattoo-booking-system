from fastapi import Header, HTTPException, Request
from app.core.config import API_SECRET_KEY

def check_api_key(x_api_key: str = Header(None), request: Request = None):
    api_key = x_api_key or request.query_params.get("api_key")
    print(f"🔍 Received API Key: {api_key}")
    
    if api_key is None:
        raise HTTPException(status_code=403, detail="❌ Missing API key.")
    if api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="❌ Invalid API key.")
