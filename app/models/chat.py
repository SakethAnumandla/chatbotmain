"""
Domain Models
Core business entities and data structures
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Chat message roles"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class ChatMessage(BaseModel):
    """Represents a single message in the conversation"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    function_call: Optional[Dict[str, Any]] = None
    name: Optional[str] = None  # For function messages


class ConversationContext(BaseModel):
    """Maintains conversation state and history"""
    session_id: str
    user_id: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def add_message(self, role: MessageRole, content: str, **kwargs) -> None:
        """Add a message to the conversation"""
        message = ChatMessage(role=role, content=content, **kwargs)
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def get_messages_for_api(self) -> List[Dict[str, Any]]:
        """Convert messages to OpenAI API format"""
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                **({"name": msg.name} if msg.name else {}),
                **({"function_call": msg.function_call} if msg.function_call else {})
            }
            for msg in self.messages
        ]
    
    def clear_old_messages(self, keep_last: int = 20) -> None:
        """Keep only the most recent messages to manage context window"""
        if len(self.messages) > keep_last:
            # Always keep system messages
            system_messages = [msg for msg in self.messages if msg.role == MessageRole.SYSTEM]
            recent_messages = [msg for msg in self.messages if msg.role != MessageRole.SYSTEM][-keep_last:]
            self.messages = system_messages + recent_messages


class ChatRequest(BaseModel):
    """Incoming chat request from user"""
    session_id: Optional[str] = None
    message: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Outgoing chat response to user"""
    session_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    suggested_queries: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class FunctionDefinition(BaseModel):
    """OpenAI function definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
