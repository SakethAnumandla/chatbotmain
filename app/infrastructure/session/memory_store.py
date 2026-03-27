"""
In-Memory Session Store Implementation
Simple session storage for development and testing
"""
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.infrastructure.session.base import SessionStore
from app.models.chat import ConversationContext
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MemorySessionStore(SessionStore):
    """In-memory session storage (not recommended for production)"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize in-memory session store
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self._store: Dict[str, tuple[ConversationContext, datetime]] = {}
        logger.warning("Using in-memory session store - not suitable for production!")
    
    async def get(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve a session from memory"""
        self._cleanup_expired()
        
        if session_id in self._store:
            context, expires_at = self._store[session_id]
            if datetime.utcnow() < expires_at:
                return context
            else:
                # Expired
                del self._store[session_id]
        return None
    
    async def set(self, session_id: str, context: ConversationContext, ttl: Optional[int] = None) -> bool:
        """Store or update a session in memory"""
        ttl = ttl or self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        self._store[session_id] = (context, expires_at)
        logger.debug(f"Session {session_id} stored in memory with TTL {ttl}s")
        return True
    
    async def delete(self, session_id: str) -> bool:
        """Delete a session from memory"""
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False
    
    async def exists(self, session_id: str) -> bool:
        """Check if a session exists in memory"""
        self._cleanup_expired()
        return session_id in self._store
    
    def _cleanup_expired(self):
        """Remove expired sessions"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, (_, expires_at) in self._store.items()
            if now >= expires_at
        ]
        for key in expired_keys:
            del self._store[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired sessions")
