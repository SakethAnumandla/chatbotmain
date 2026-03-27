# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                     │
│         (Web, Mobile, Desktop, Third-party Apps)             │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Server                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Presentation Layer (routes/)                  │  │
│  │  • REST Endpoints  • Request Validation               │  │
│  │  • Response Formatting  • Error Handling              │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐  │
│  │      Application Layer (services/)                    │  │
│  │  • ChatbotService (Orchestration)                     │  │
│  │  • OpenAIService (AI Processing)                      │  │
│  │  • Function Definitions                               │  │
│  └────┬─────────────────────────────────────────┬────────┘  │
│       │                                          │            │
│  ┌────┴────────────────┐              ┌─────────┴────────┐  │
│  │  Domain Layer       │              │  Infrastructure   │  │
│  │  (models/)          │              │  Layer            │  │
│  │  • ChatMessage      │              │  (infrastructure/)│  │
│  │  • Conversation     │              │  • Session Store  │  │
│  │  • DTOs             │              │  • API Clients    │  │
│  └─────────────────────┘              └──────┬────────────┘  │
└─────────────────────────────────────────────┼───────────────┘
                                               │
                     ┌─────────────────────────┼─────────────────────┐
                     │                         │                     │
                     ▼                         ▼                     ▼
           ┌──────────────────┐    ┌────────────────────┐  ┌──────────────┐
           │  OpenAI API      │    │  Platform APIs     │  │ In-Memory    │
           │  • GPT-4o        │    │  • Products        │  │ Session Store│
           │  • Function Call │    │  • Orders          │  │ (Short-Lived)│
           │                  │    │  • Analytics       │  │              │
           └──────────────────┘    └────────────────────┘  └──────────────┘
```

## Detailed Component Architecture

### 1. Presentation Layer (FastAPI Routes)
```
app/routes/chatbot_routes.py
│
├─ POST   /api/v1/chatbot/sessions          → Create Session (optional)
├─ GET    /api/v1/chatbot/sessions/:id      → Get Session
├─ DELETE /api/v1/chatbot/sessions/:id      → Delete Session
├─ POST   /api/v1/chatbot/sessions/:id/clear → Clear History
├─ POST   /api/v1/chatbot/chat              → Send Message
└─ GET    /api/v1/chatbot/health            → Health Check
```

### 2. Application Layer (Business Logic)

**ChatbotService** - Main orchestrator
```
┌────────────────────────────────────┐
│      ChatbotService                │
├────────────────────────────────────┤
│ + process_message()                │
│ + create_session()                 │
│ + get_session()                    │
│ + delete_session()                 │
│ + clear_session_history()          │
└────────────────────────────────────┘
         │
         ├─── Uses ───► SessionStore (In-Memory)
         └─── Uses ───► OpenAIService
```

**OpenAIService** - AI processing
```
┌────────────────────────────────────┐
│      OpenAIService                 │
├────────────────────────────────────┤
│ + chat()                           │
│ + _execute_function()              │
├────────────────────────────────────┤
│ Features:                          │
│ • Function calling loop            │
│ • Context management               │
│ • Error handling                   │
│ • Token optimization               │
└────────────────────────────────────┘
         │
         ├─── Calls ───► OpenAI API
         └─── Calls ───► PlatformAPIClient
```

### 3. Domain Layer (Core Models)

```
ConversationContext
├─ session_id: str
├─ user_id: Optional[str]
├─ messages: List[ChatMessage]
├─ metadata: Dict
├─ created_at: datetime
└─ updated_at: datetime

ChatMessage
├─ role: MessageRole (system/user/assistant/function)
├─ content: str
├─ timestamp: datetime
└─ function_call: Optional[Dict]
```

### 4. Infrastructure Layer

**Session Storage**
```
┌─────────────────────────┐
│   SessionStore (ABC)    │
├─────────────────────────┤
│ + get()                 │
│ + set()                 │
│ + delete()              │
│ + exists()              │
└─────────────────────────┘
         △
         │ implements
      ┌───────────┐
      │ In-Memory │
      │   Store   │
      └───────────┘
```

**Platform API Client**
```
PlatformAPIClient
│
├─ Product APIs
│  ├─ search_products()
│  ├─ get_product_details()
│  ├─ get_product_stock()
│  └─ get_low_stock_products()
│
├─ Order APIs
│  ├─ create_order()
│  ├─ get_order_status()
│  ├─ update_order()
│  └─ cancel_order()
│
├─ Report APIs
│  ├─ get_sales_report()
│  ├─ get_products_report()
│  ├─ get_stock_report()
│  ├─ get_top_proformas_report()
│  ├─ get_recent_orders_report()
│  ├─ get_customers_report()
│  └─ get_company_health_report()
│
└─ Customer APIs
   ├─ get_customer_info()
   └─ get_customer_orders()
```

## Data Flow

### Message Processing Flow

```
1. Client sends message
      │
      ▼
2. FastAPI route receives request
      │
      ├─ Validate request (Pydantic)
      ├─ Check rate limit
      └─ Parse JSON
      │
      ▼
3. ChatbotService.process_message()
      │
      ├─ Auto-create session when session_id missing
      ├─ Get/Create session context
      ├─ Add user message to context
      ├─ Generate 4 suggested follow-up queries
      └─ Call OpenAIService.chat()
      │
      ▼
4. OpenAIService.chat()
      │
      ├─ Prepare messages with system prompt
      ├─ Send to OpenAI API with functions
      │
      ▼
5. OpenAI Response
      │
      ├─ Text response? → Return to user
      │
      └─ Function call?
           │
           ├─ Parse function name & arguments
           ├─ Execute via PlatformAPIClient
           ├─ Get function result
           ├─ Send result back to OpenAI
           └─ Loop until final response
      │
      ▼
6. Save conversation context to session store
      │
      ▼
7. Return response to client (`message`, `session_id`, `suggested_queries`, metadata)
```

### Function Calling Flow

```
User: "Show me laptops under 50000"
  │
  ├─► OpenAI decides: search_products()
  │   with arguments: {query: "laptops", max_price: 50000}
  │
  ├─► Execute: platform_client.search_products(query="laptops", max_price=50000)
  │
  ├─► Platform API returns: {products: [...15 laptops...]}
  │
  ├─► Send result to OpenAI
  │
  └─► OpenAI generates natural response:
      "I found 15 laptops under ₹50,000. Here are the top options..."
```

## Session Management Architecture

```
Session Lifecycle:

1. Create Session
   ┌─────────────────┐
   │ Generate UUID   │
   │ session_id      │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │ Create Context  │
   │ with metadata   │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
      │ Store in Memory │
   │ with TTL        │
   └─────────────────┘

2. Message Exchange
   ┌──────────────────┐
   │ Retrieve Context │
   │ from cache       │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Add messages     │
   │ to conversation  │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Process with AI  │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Update Context   │
   │ Save to cache    │
   └──────────────────┘

3. Cleanup
   ┌──────────────────┐
   │ Auto-expire      │
   │ after TTL        │
   └────────┬─────────┘
            │
     OR     │
            ▼
   ┌──────────────────┐
   │ Manual delete    │
   │ by user/system   │
   └──────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────┐
│         Client Request              │
└────────────┬────────────────────────┘
             │
             ▼
    ┌────────────────┐
      │  Rate Limiter  │ ← In-memory backend
    │  20 req/min    │
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │  CORS Check    │ ← Configured origins
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │  Input Valid.  │ ← Pydantic models
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │  Auth Header   │ ← Bearer token
    │  for Platform  │    for API calls
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │  Error Handle  │ ← Safe error messages
    │  No leak info  │
    └────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
```
┌────────────┐     ┌────────────┐     ┌────────────┐
│  Instance  │     │  Instance  │     │  Instance  │
│     1      │     │     2      │     │     3      │
└─────┬──────┘     └─────┬──────┘     └─────┬──────┘
      │                  │                  │
      └──────────────────┼──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   Load Balancer  │
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Shared Stateless │
              │ app instances;   │
              │ short-lived local│
              │ session contexts │
              └──────────────────┘
```

### Performance Optimizations
- **Async I/O**: Async HTTP clients for non-blocking operations
- **Connection Pooling**: Reuse HTTP connections
- **Session TTL**: Auto-expire old sessions
- **Context Window**: Keep only recent messages
- **Ephemeral State**: In-memory session context
- **Rate Limiting**: Prevent abuse

## Deployment Architecture (Production)

```
                    ┌─────────────┐
                    │   Nginx     │
                    │   (Proxy)   │
                    └──────┬──────┘
                           │ HTTPS
                ┌──────────┼──────────┐
                │          │          │
         ┌──────▼─────┐ ┌─▼──────────▼┐
         │  FastAPI   │ │   FastAPI   │
         │  Instance  │ │   Instance  │
         │  (Uvicorn) │ │  (Uvicorn)  │
         └──────┬─────┘ └─────┬───────┘
                │              │
                └──────┬───────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
      ┌─────────┐   ┌───▼────┐   ┌───▼────┐
      │ In-App  │   │OpenAI  │   │Platform│
      │ Memory  │   │  API   │   │  APIs  │
      └─────────┘   └────────┘   └────────┘
```

## Technology Stack

```
┌────────────────────────────────────────┐
│         Application Layer              │
│  • FastAPI 0.110 - Web framework       │
│  • Pydantic 2.5 - Data validation      │
│  • OpenAI 1.12 - AI integration        │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│      Infrastructure Layer              │
│  • In-memory store - Session state      │
│  • HTTPX 0.26 - Async HTTP client      │
│  • Python-dotenv - Configuration       │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│        Cross-cutting Concerns          │
│  • CORSMiddleware - CORS handling      │
│  • SlowAPI - Rate limiting             │
│  • Python-JSON-Logger - Logging        │
└────────────────────────────────────────┘
```

## Key Design Decisions

1. **Clean Architecture**: Separation of concerns, testability, maintainability
2. **Repository Pattern**: Abstract session storage for flexibility
3. **Function Calling**: Let AI decide which APIs to call
4. **Async Operations**: Non-blocking I/O for better performance
5. **Type Safety**: Pydantic for validation and documentation
6. **Ephemeral Sessions**: Auto-expiring in-memory conversation context
7. **Rate Limiting**: Protect against abuse
8. **Comprehensive Logging**: Audit trail and debugging
