"""
FastAPI Application Factory
Main application setup and initialization
"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from config import settings
from app.utils.logger import setup_logging, get_logger
from app.infrastructure.session import create_session_store
from app.infrastructure.api.platform_client import PlatformAPIClient
from app.services.chatbot_service import ChatbotService
from app.routes.chatbot_routes import chatbot_router, init_routes
from app.utils.rate_limit import limiter

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Application factory for FastAPI app
    
    Returns:
        Configured FastAPI application
    """
    # Setup logging first
    setup_logging()
    
    # Initialize infrastructure first so lifecycle can close resources cleanly.
    session_store = create_session_store()
    platform_client = PlatformAPIClient()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            try:
                await platform_client.close()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

    # Create FastAPI app
    app = FastAPI(
        title="Bizwy Chatbot AI Server",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Rate limiting
    if settings.rate_limit_enabled:
        app.state.limiter = limiter
        limiter.default_limits = [f"{settings.rate_limit_per_minute}/minute"]
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        logger.info(f"Rate limiting enabled: {settings.rate_limit_per_minute} req/min")
    
    # Initialize service
    chatbot_service = ChatbotService(
        session_store=session_store,
        platform_client=platform_client
    )
    
    # Initialize routes with service
    init_routes(chatbot_service)
    
    # Register routers
    app.include_router(chatbot_router)
    
    # Root endpoint
    @app.get('/')
    async def index():
        return {
            "service": "Bizwy Chatbot AI Server",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "health": "/api/v1/chatbot/health",
                "chat": "/api/v1/chatbot/chat",
                "sessions": "/api/v1/chatbot/sessions"
            }
        }
    
    logger.info("Application initialized successfully")
    return app


# Expose ASGI app for standard uvicorn startup: uvicorn app:app
app = create_app()


if __name__ == '__main__':
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        reload=False
    )
