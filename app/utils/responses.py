"""
Response Utilities
Standardized API response formatting
"""
from typing import Any, Optional, Dict
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = 200
) -> JSONResponse:
    """
    Create a standardized success response
    
    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code
        
    Returns:
        FastAPI JSON response
    """
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    if message:
        response["message"] = message
    
    return JSONResponse(content=jsonable_encoder(response), status_code=status_code)


def error_response(
    message: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a standardized error response
    
    Args:
        message: Error message
        status_code: HTTP status code
        details: Optional error details
        
    Returns:
        FastAPI JSON response
    """
    response = {
        "success": False,
        "error": {
            "message": message,
            "code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    if details:
        response["error"]["details"] = details
    
    return JSONResponse(content=jsonable_encoder(response), status_code=status_code)
