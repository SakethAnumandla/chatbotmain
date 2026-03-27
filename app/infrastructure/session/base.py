"""
Session Management Interface
Abstraction for different session storage backends
"""
from abc import ABC, abstractmethod
from typing import Optional
from app.models.chat import ConversationContext


class SessionStore(ABC):
    """Abstract base class for session storage"""
    
    @abstractmethod
    async def get(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve a session by ID"""
        pass
    
    @abstractmethod
    async def set(self, session_id: str, context: ConversationContext, ttl: Optional[int] = None) -> bool:
        """Store or update a session"""
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete a session"""
        pass
    
    @abstractmethod
    async def exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        pass
