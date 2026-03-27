"""
Chatbot Service
Business logic layer that orchestrates AI, session, and API interactions
"""
import uuid
from typing import Optional
from app.models.chat import ConversationContext, ChatRequest, ChatResponse
from app.services.openai_service import OpenAIService
from app.infrastructure.session.base import SessionStore
from app.infrastructure.api.platform_client import PlatformAPIClient
from app.utils.logger import get_logger
from app.utils.exceptions import SessionNotFoundException

logger = get_logger(__name__)


class ChatbotService:
    """
    Main service for chatbot operations
    Coordinates between session management, AI processing, and API calls
    """
    
    def __init__(
        self,
        session_store: SessionStore,
        platform_client: PlatformAPIClient
    ):
        """
        Initialize chatbot service
        
        Args:
            session_store: Session storage backend
            platform_client: Platform API client
        """
        self.session_store = session_store
        self.platform_client = platform_client
        self.openai_service = OpenAIService(platform_client)
        logger.info("Chatbot service initialized")
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a user message and return AI response
        
        Args:
            request: Chat request with message and session info
            
        Returns:
            Chat response with AI reply
        """
        session_id = request.session_id or str(uuid.uuid4())
        session_created = request.session_id is None
        
        try:
            # Get or create conversation context
            context = await self._get_or_create_context(session_id, request.user_id)
            
            # Update metadata if provided
            if request.metadata:
                context.metadata.update(request.metadata)
            
            logger.info(f"Processing message for session {session_id}: {request.message[:50]}...")
            
            # Get AI response
            ai_response = await self.openai_service.chat(context, request.message)

            # Generate follow-up suggestions for better UX.
            suggested_queries = self._build_suggested_queries(request.message)
            
            # Save updated context
            await self.session_store.set(session_id, context)
            
            # Create response
            response = ChatResponse(
                session_id=session_id,
                message=ai_response,
                suggested_queries=suggested_queries,
                metadata={
                    "message_count": len(context.messages),
                    "user_id": context.user_id,
                    "session_created": session_created,
                    "company_id": context.metadata.get("company_id")
                }
            )
            
            logger.info(f"Response generated for session {session_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {e}", exc_info=True)
            raise
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new chat session
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            New session ID
        """
        session_id = str(uuid.uuid4())
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id
        )
        
        await self.session_store.set(session_id, context)
        logger.info(f"Created new session: {session_id}")
        
        return session_id
    
    async def get_session(self, session_id: str) -> ConversationContext:
        """
        Retrieve an existing session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Conversation context
            
        Raises:
            SessionNotFoundException: If session doesn't exist
        """
        context = await self.session_store.get(session_id)
        if not context:
            raise SessionNotFoundException(session_id)
        return context

    def _build_suggested_queries(self, user_message: str) -> list[str]:
        """
        Build exactly 4 suggested follow-up queries based on user intent.

        This is deterministic and fast, so it does not add model latency.
        """
        text = user_message.lower()

        sales_keywords = ("sales", "report", "revenue", "profit", "analytics")
        stock_keywords = ("stock", "inventory", "low stock", "out of stock")
        order_keywords = ("order", "place order", "cancel", "status", "tracking")
        product_keywords = ("product", "item", "catalog", "search", "details")

        if any(k in text for k in sales_keywords):
            suggestions = [
                "Show product-wise sales report for this month",
                "Compare this month sales with last month",
                "Show top customers by purchase value",
                "Show recent orders with completed status",
            ]
        elif any(k in text for k in stock_keywords):
            suggestions = [
                "Show low stock items with threshold 5",
                "Show out of stock products only",
                "Show stock valuation summary",
                "Suggest what to restock first",
            ]
        elif any(k in text for k in order_keywords):
            suggestions = [
                "Show my recent orders",
                "Check status of order ORD-001",
                "Find products available for quick reorder",
                "Show top proformas for this week",
            ]
        elif any(k in text for k in product_keywords):
            suggestions = [
                "Show details for a specific product",
                "Check stock for that product",
                "Find similar products in this category",
                "Create an order with selected products",
            ]
        else:
            suggestions = [
                "Show my company sales report for this month",
                "Show low stock products",
                "Show recent orders",
                "Show company health summary",
            ]

        return suggestions[:4]
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted successfully
        """
        result = await self.session_store.delete(session_id)
        if result:
            logger.info(f"Deleted session: {session_id}")
        return result
    
    async def clear_session_history(self, session_id: str) -> bool:
        """
        Clear conversation history but keep session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if cleared successfully
        """
        context = await self.get_session(session_id)
        context.messages = []
        await self.session_store.set(session_id, context)
        logger.info(f"Cleared history for session: {session_id}")
        return True
    
    async def _get_or_create_context(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> ConversationContext:
        """
        Get existing context or create new one
        
        Args:
            session_id: Session identifier
            user_id: Optional user identifier
            
        Returns:
            Conversation context
        """
        context = await self.session_store.get(session_id)
        
        if not context:
            logger.info(f"Session {session_id} not found, creating new context")
            context = ConversationContext(
                session_id=session_id,
                user_id=user_id
            )
            await self.session_store.set(session_id, context)
        
        return context
