# Bizwy Chatbot AI Server

A production-grade AI chatbot server for B2B PIMS (Product Information Management System) and e-commerce platform. Built with FastAPI, OpenAI, and Clean Architecture principles.

## 🎯 Features

### For Customers
- **Product Discovery**: Search and browse products with intelligent filters
- **Product Information**: Get detailed product specifications and availability
- **Order Management**: Place orders, track status, and manage purchases
- **Order History**: View past orders and purchase patterns

### For Business Owners
- **Sales Analytics**: Comprehensive sales reports and trends
- **Inventory Intelligence**: Smart low-stock alerts and restocking suggestions
- **Seasonal Recommendations**: Product suggestions based on seasons, festivals, and events
- **Business Insights**: Data-driven analysis and actionable recommendations

### Technical Features
- **Session Management**: In-memory short-lived conversation context
- **Function Calling**: OpenAI function calling for dynamic API interactions
- **Clean Architecture**: Separation of concerns with proper layering
- **Type Safety**: Pydantic models for validation
- **Production Ready**: Logging, error handling, rate limiting, CORS
- **Scalable**: Async operations with clean service boundaries

## 📁 Project Structure

```
bizwy-chatbot/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py                 # Domain models (ChatMessage, ConversationContext)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chatbot_service.py      # Business logic orchestration
│   │   ├── openai_service.py       # OpenAI integration with function calling
│   │   └── function_definitions.py # AI function definitions
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── session/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Session storage interface
│   │   │   └── memory_store.py     # In-memory implementation
│   │   └── api/
│   │       ├── __init__.py
│   │       └── platform_client.py  # Platform API client
│   ├── routes/
│   │   ├── __init__.py
│   │   └── chatbot_routes.py       # FastAPI endpoints
│   └── utils/
│       ├── __init__.py
│       ├── logger.py               # Logging configuration
│       ├── exceptions.py           # Custom exceptions
│       └── responses.py            # Response utilities
├── app.py                          # FastAPI application factory
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore
└── README.md
```

## 🏗️ Architecture

### Clean Architecture Layers

1. **Presentation Layer** (`routes/`)
  - FastAPI REST endpoints
   - Request validation
   - Response formatting

2. **Application Layer** (`services/`)
   - Business logic
   - Service orchestration
   - Use case implementation

3. **Domain Layer** (`models/`)
   - Core business entities
   - Domain models
   - Business rules

4. **Infrastructure Layer** (`infrastructure/`)
   - External integrations (OpenAI, Platform APIs)
  - Session storage (In-Memory)
   - Data persistence

### Key Design Patterns

- **Repository Pattern**: Session storage abstraction
- **Factory Pattern**: Session store creation
- **Dependency Injection**: Service composition
- **Strategy Pattern**: Multiple session storage backends
- **Adapter Pattern**: Platform API client

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key
- Access to your platform APIs

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd "d:\Projects\Bizwy-PIMS\bizwy chatbot"
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   ```powershell
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   
   # Command Prompt
   venv\Scripts\activate.bat
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env with your configuration
   ```

6. **Update `.env` file** with your credentials:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4o
   PLATFORM_API_BASE_URL=https://your-platform.com/api/v1
   PLATFORM_API_KEY=your_platform_api_key
   ```

### Running the Server

#### Standard uvicorn startup (recommended)
```bash
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

#### Production-style startup (no reload)
```bash
uvicorn app:app --host 0.0.0.0 --port 5000
```

The server will start at `http://localhost:5000` (or the `APP_PORT` you choose).

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api/v1/chatbot
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "chatbot-ai-server"
  },
  "message": "Service is running",
  "timestamp": "2026-03-07T10:30:00Z"
}
```

#### 2. Create Session
```http
POST /sessions
```

**Request Body** (optional):
```json
{
  "user_id": "customer123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "message": "Session created successfully",
  "timestamp": "2026-03-07T10:30:00Z"
}
```

#### 3. Send Chat Message
```http
POST /chat
```

**Request Body:**
```json
{
  "message": "Show me laptops under ₹50000",
  "user_id": "customer123",
  "metadata": {
    "source": "web"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "I found 15 laptops under ₹50,000. Here are some popular options:\n\n1. Dell Inspiron 15 - ₹45,999\n2. HP Pavilion 14 - ₹48,500\n3. Lenovo IdeaPad 3 - ₹42,999\n\nWould you like more details on any of these?",
    "timestamp": "2026-03-07T10:30:15Z",
    "suggested_queries": [
      "Show details for a specific product",
      "Check stock for that product",
      "Find similar products in this category",
      "Create an order with selected products"
    ],
    "metadata": {
      "message_count": 4,
      "user_id": "customer123",
      "session_created": true,
      "company_id": 1
    }
  },
  "timestamp": "2026-03-07T10:30:15Z"
}
```

`session_id` is optional on first message. If omitted, the server auto-creates it and returns it in the response.
For report queries, frontend should send `metadata.company_id` so report APIs are scoped correctly.

#### 4. Get Session Details
```http
GET /sessions/{session_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "customer123",
    "message_count": 4,
    "metadata": {},
    "created_at": "2026-03-07T10:30:00Z",
    "updated_at": "2026-03-07T10:35:00Z"
  }
}
```

#### 5. Clear Session History
```http
POST /sessions/{session_id}/clear
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "message": "Session history cleared successfully"
}
```

#### 6. Delete Session
```http
DELETE /sessions/{session_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "message": "Session deleted successfully"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o` |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `PLATFORM_API_BASE_URL` | Your platform API URL | Required |
| `PLATFORM_API_KEY` | Platform API authentication key | Required |
| `SESSION_TTL` | Session timeout in seconds | `3600` |
| `APP_HOST` | Server host | `0.0.0.0` |
| `APP_PORT` | Server port | `5000` |
| `APP_ENV` | Runtime environment | `development` |
| `APP_DEBUG` | Reload/debug mode | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RATE_LIMIT_PER_MINUTE` | Max requests per minute | `20` |

## 🤖 AI Capabilities

The chatbot uses OpenAI's function calling to intelligently interact with your platform APIs:

### Available Functions

1. **search_products** - Search product catalog
2. **get_product_details** - Get specific product information
3. **check_product_stock** - Check product availability
4. **get_low_stock_products** - Get low inventory items
5. **create_order** - Place a new order
6. **get_order_status** - Track order status
7. **cancel_order** - Cancel an order
8. **get_sales_report** - Tenant-scoped sales report
9. **get_products_report** - Product report for owner insights
10. **get_stock_report** - Stock and valuation report
11. **get_top_proformas_report** - Top proformas view
12. **get_recent_orders_report** - Recent orders report
13. **get_customers_report** - Customer analytics report
14. **get_company_health_report** - Company KPI summary
15. **get_customer_orders** - Customer order history

### Example Conversations

**Customer Use Case:**
```
User: "I need a laptop for design work under 60k"
Bot: [Calls search_products] "I found 12 laptops suitable for design work..."

User: "Tell me more about the Dell one"
Bot: [Calls get_product_details] "The Dell Inspiron 15 features..."

User: "Is it in stock?"
Bot: [Calls check_product_stock] "Yes, 5 units available..."

User: "I'll take it"
Bot: "Great! Let me help you place the order..."
```

**Owner Use Case:**
```
Owner: "Show me sales for last month"
Bot: [Calls get_sales_report] "Here's your sales performance for February..."

Owner: "Which products are running low on stock?"
Bot: [Calls get_stock_report] "You have 8 products with low inventory..."

Owner: "How healthy is my company this month?"
Bot: [Calls get_company_health_report] "Here are your key KPIs and trends..."
```

## 🔒 Security Features

- **API Authentication**: Bearer token authentication for platform APIs
- **Rate Limiting**: Configurable request limits per IP
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Comprehensive exception handling
- **Logging**: Audit trail for all operations

## 📊 Monitoring & Logging

Logs are stored in `logs/chatbot.log` with:
- Structured JSON format (production)
- Human-readable format (development)
- Rotating file handlers
- Different log levels per module

## 🧪 Testing

For complete Postman setup and test scenarios, see `POSTMAN_TESTING_GUIDE.md`.

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## 🚀 Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

Build and run:
```bash
docker build -t bizwy-chatbot .
docker run -p 5000:5000 --env-file .env bizwy-chatbot
```

### Production Checklist

- [ ] Set `APP_ENV=production` and `APP_DEBUG=False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up reverse proxy (Nginx)
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Monitor with application monitoring tools
- [ ] Set resource limits (CPU, memory)

## 🤝 Integration Guide

### Integrating with Your Platform

1. **Update Platform API Client** (`app/infrastructure/api/platform_client.py`):
   - Modify endpoint paths to match your API structure
   - Adjust authentication headers if needed
   - Add any custom error handling

2. **Configure API Base URL** in `.env`:
   ```env
   PLATFORM_API_BASE_URL=https://your-api.com/api/v1
   PLATFORM_API_KEY=your_api_key
   ```

3. **Test API Integration**:
   ```python
   # Test with a simple request
   curl -X POST http://localhost:5000/api/v1/chatbot/chat \
     -H "Content-Type: application/json" \
     -d '{"session_id":"test-123", "message":"Show products"}'
   ```

## 📝 Extending Functionality

### Adding New Functions

1. **Define Function** in `app/services/function_definitions.py`:
   ```python
   {
       "name": "your_function_name",
       "description": "What this function does",
       "parameters": {...}
   }
   ```

2. **Add Platform API Method** in `app/infrastructure/api/platform_client.py`:
   ```python
   async def your_api_method(self, params):
       return await self._request("GET", "/your-endpoint", params=params)
   ```

3. **Route Function Call** in `app/services/openai_service.py`:
   ```python
   elif function_name == "your_function_name":
       result = await self.platform_client.your_api_method(**arguments)
   ```

## 🐛 Troubleshooting

### Common Issues

**OpenAI API Error:**
```
Solution: Verify API key in .env
Check OPENAI_API_KEY is valid and has credits
```

**Platform API Timeout:**
```
Solution: Increase timeout in .env
PLATFORM_API_TIMEOUT=60
```

## 📄 License

This project is proprietary software for Bizwy PIMS platform.

## 👥 Support

For issues and questions:
- Create an issue in the repository
- Contact the development team
- Check logs in `logs/chatbot.log`

## 🎉 Acknowledgments

- Built with FastAPI and OpenAI
- Follows Clean Architecture principles
- Designed for production workloads
