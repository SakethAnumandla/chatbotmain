"""
Custom Exceptions
Domain-specific exceptions for better error handling
"""


class ChatbotException(Exception):
    """Base exception for chatbot errors"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class SessionNotFoundException(ChatbotException):
    """Raised when a session cannot be found"""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session not found: {session_id}",
            status_code=404,
            details={"session_id": session_id}
        )


class PlatformAPIException(ChatbotException):
    """Raised when platform API calls fail"""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(
            message=f"Platform API error: {message}",
            status_code=status_code
        )


class OpenAIException(ChatbotException):
    """Raised when OpenAI API calls fail"""
    def __init__(self, message: str):
        super().__init__(
            message=f"OpenAI API error: {message}",
            status_code=503
        )


class ValidationException(ChatbotException):
    """Raised when request validation fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=400,
            details=details
        )


class RateLimitException(ChatbotException):
    """Raised when rate limit is exceeded"""
    def __init__(self):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=429
        )
