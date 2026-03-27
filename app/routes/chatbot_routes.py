"""
FastAPI Routes
RESTful endpoints for chatbot interactions
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, ValidationError

from app.models.chat import ChatRequest
from app.services.chatbot_service import ChatbotService
from app.utils.responses import success_response, error_response
from app.utils.exceptions import ChatbotException, SessionNotFoundException
from app.utils.rate_limit import limiter
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create router
chatbot_router = APIRouter(prefix='/api/v1/chatbot', tags=['chatbot'])

# Global service instance (initialized in app factory)
chatbot_service: ChatbotService = None


class CreateSessionRequest(BaseModel):
    """Create session request body"""
    user_id: Optional[str] = None


def init_routes(service: ChatbotService):
    """Initialize routes with service instance"""
    global chatbot_service
    chatbot_service = service


@chatbot_router.get('/health')
async def health_check():
    """Health check endpoint"""
    return success_response(
        data={"status": "healthy", "service": "chatbot-ai-server"},
        message="Service is running"
    )


@chatbot_router.post('/sessions')
@limiter.limit("10/minute")
async def create_session(request: Request, payload: Optional[CreateSessionRequest] = None):
    """
    Create a new chat session
    
    Request Body (optional):
        {
            "user_id": "string"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "session_id": "uuid"
            }
        }
    """
    try:
        user_id = payload.user_id if payload else None
        
        session_id = await chatbot_service.create_session(user_id)
        
        return success_response(
            data={"session_id": session_id},
            message="Session created successfully",
            status_code=201
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        return error_response("Failed to create session", status_code=500)


@chatbot_router.get('/sessions/{session_id}')
async def get_session(session_id: str):
    """
    Get session details
    
    Response:
        {
            "success": true,
            "data": {
                "session_id": "uuid",
                "message_count": 10,
                "created_at": "timestamp",
                "updated_at": "timestamp"
            }
        }
    """
    try:
        context = await chatbot_service.get_session(session_id)
        
        return success_response(
            data={
                "session_id": context.session_id,
                "user_id": context.user_id,
                "message_count": len(context.messages),
                "metadata": context.metadata,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat()
            }
        )
    except SessionNotFoundException as e:
        return error_response(e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error retrieving session: {e}", exc_info=True)
        return error_response("Failed to retrieve session", status_code=500)


@chatbot_router.delete('/sessions/{session_id}')
async def delete_session(session_id: str):
    """
    Delete a chat session
    
    Response:
        {
            "success": true,
            "message": "Session deleted successfully"
        }
    """
    try:
        result = await chatbot_service.delete_session(session_id)
        
        if result:
            return success_response(
                data={"session_id": session_id},
                message="Session deleted successfully"
            )
        else:
            return error_response("Session not found", status_code=404)
            
    except Exception as e:
        logger.error(f"Error deleting session: {e}", exc_info=True)
        return error_response("Failed to delete session", status_code=500)


@chatbot_router.post('/sessions/{session_id}/clear')
async def clear_session_history(session_id: str):
    """
    Clear conversation history for a session
    
    Response:
        {
            "success": true,
            "message": "Session history cleared"
        }
    """
    try:
        await chatbot_service.clear_session_history(session_id)
        
        return success_response(
            data={"session_id": session_id},
            message="Session history cleared successfully"
        )
    except SessionNotFoundException as e:
        return error_response(e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error clearing session history: {e}", exc_info=True)
        return error_response("Failed to clear session history", status_code=500)


@chatbot_router.post('/chat')
@limiter.limit("20/minute")
async def chat(request: Request):
    """
    Send a message and get AI response
    
    Request Body:
        {
            "session_id": "uuid" (optional on first message),
            "message": "string",
            "user_id": "string" (optional),
            "metadata": {} (optional)
        }
    
    Response:
        {
            "success": true,
            "data": {
                "session_id": "uuid",
                "message": "AI response",
                "timestamp": "ISO timestamp",
                "metadata": {
                    "session_created": true/false
                }
            }
        }
    """
    try:
        data = await request.json()
        
        if not data:
            return error_response("Request body is required", status_code=400)
        
        # Validate request
        try:
            chat_request = ChatRequest(**data)
        except ValidationError as e:
            return error_response(
                "Invalid request data",
                status_code=400,
                details=e.errors()
            )
        
        # Process message
        response = await chatbot_service.process_message(chat_request)
        
        return success_response(
            data=response.model_dump()
        )
        
    except ChatbotException as e:
        return error_response(e.message, status_code=e.status_code, details=e.details)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return error_response(
            "An error occurred while processing your message",
            status_code=500
        )


