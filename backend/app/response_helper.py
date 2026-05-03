from typing import Any, Dict, Optional

def success_response(
    message: str,
    data: Any = None,
    meta: Optional[Dict] = None
) -> Dict:
    """Standard success response format"""
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    if meta:
        response["meta"] = meta
    
    return response

def error_response(
    message: str,
    error: Optional[str] = None,
    errors: Optional[list] = None
) -> Dict:
    """Standard error response format"""
    response = {
        "success": False,
        "message": message
    }
    
    if error:
        response["error"] = error
    
    if errors:
        response["errors"] = errors
    
    return response