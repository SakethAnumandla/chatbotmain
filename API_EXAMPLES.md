# Example API Requests for Testing

## 0. First Message (Auto Session Create)

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me available laptops",
    "user_id": "customer123",
    "metadata": {
      "company_id": 1
    }
  }'
```

Use the returned `data.session_id` for follow-up messages.

## 1. Create a New Session

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "customer123"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

## 2. Send a Chat Message

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Show me available laptops",
    "user_id": "customer123"
  }'
```

---

## 3. Product Search

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "I need a laptop for design work under 60000 rupees"
  }'
```

---

## 4. Product Details

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Tell me more about product ID: PROD123"
  }'
```

---

## 5. Check Stock

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Is product PROD123 in stock?"
  }'
```

---

## 6. Place Order

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "I want to order 2 units of product PROD123"
  }'
```

---

## 7. Check Order Status

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "What is the status of order ORD456?"
  }'
```

---

## 8. Sales Analytics (Business Owner)

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Show my company sales report for this month",
    "metadata": {
      "company_id": 1
    }
  }'
```

---

## 9. Low Stock Products

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Which products are running low on stock?"
  }'
```

---

## 10. Seasonal Recommendations

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Suggest products to stock for Diwali festival"
  }'
```

---

## 11. Inventory Analysis

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Show stock report with low stock threshold 5",
    "metadata": {
      "company_id": 1
    }
  }'
```

---

## Chat Response Notes

`POST /chat` returns:
- `data.session_id`
- `data.message`
- `data.suggested_queries` (always 4 follow-up suggestions)
- `data.metadata.session_created`
- `data.metadata.company_id` (if provided)

---

## 12. Get Session Details

```bash
curl -X GET http://localhost:5000/api/v1/chatbot/sessions/550e8400-e29b-41d4-a716-446655440000
```

---

## 13. Clear Session History

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/sessions/550e8400-e29b-41d4-a716-446655440000/clear
```

---

## 14. Delete Session

```bash
curl -X DELETE http://localhost:5000/api/v1/chatbot/sessions/550e8400-e29b-41d4-a716-446655440000
```

---

## 15. Health Check

```bash
curl -X GET http://localhost:5000/api/v1/chatbot/health
```

---

## PowerShell Examples

For Windows PowerShell, use `Invoke-RestMethod`:

```powershell
# Create Session
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/chatbot/sessions" -Method Post -ContentType "application/json" -Body '{"user_id": "customer123"}'
$sessionId = $response.data.session_id

# Send Message
$body = @{
    session_id = $sessionId
    message = "Show me laptops"
    user_id = "customer123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/v1/chatbot/chat" -Method Post -ContentType "application/json" -Body $body
```

---

## Python Example

```python
import requests

# Create session
response = requests.post(
    "http://localhost:5000/api/v1/chatbot/sessions",
    json={"user_id": "customer123"}
)
session_id = response.json()["data"]["session_id"]

# Send message
response = requests.post(
    "http://localhost:5000/api/v1/chatbot/chat",
    json={
        "session_id": session_id,
        "message": "Show me laptops under 50000",
        "user_id": "customer123"
    }
)
print(response.json()["data"]["message"])
```
