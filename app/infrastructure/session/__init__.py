"""
Session Store Factory
Creates in-memory session store based on configuration
"""
from app.infrastructure.session.base import SessionStore
from app.infrastructure.session.memory_store import MemorySessionStore
from config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_session_store() -> SessionStore:
    """
    Factory function to create in-memory session store.
    
    Returns:
        SessionStore: Configured session store instance
    """
    logger.info("Initializing in-memory session store")
    return MemorySessionStore(default_ttl=settings.session_ttl)
