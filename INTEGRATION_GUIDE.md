# API Integration Examples

This guide shows frontend/backend integration with the current chatbot behavior.

## Runtime Contract (Important)

- Endpoint: `POST /api/v1/chatbot/chat`
- `session_id` is optional on first request; backend auto-creates it.
- Frontend should store `data.session_id` and send it in all next requests.
- For report and analytics queries, send `metadata.company_id` from frontend context.
- Response includes `data.suggested_queries` (exactly 4 follow-up suggestions).

## JavaScript/TypeScript Integration

```javascript
class ChatbotClient {
  constructor(baseURL = 'http://localhost:5000/api/v1/chatbot', companyId = null) {
    this.baseURL = baseURL;
    this.sessionId = null;
    this.companyId = companyId;
  }

  async sendMessage(message, userId = null) {
    const payload = {
      session_id: this.sessionId,
      message,
      user_id: userId,
      metadata: this.companyId ? { company_id: this.companyId } : undefined,
    };

    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error?.message || 'Failed to send message');
    }

    // Backend returns session_id even when it auto-creates a new session.
    this.sessionId = data.data.session_id;

    return {
      message: data.data.message,
      suggestedQueries: data.data.suggested_queries || [],
      metadata: data.data.metadata || {},
    };
  }
}

// Usage
const chatbot = new ChatbotClient('http://localhost:5000/api/v1/chatbot', 1);

async function run() {
  const res = await chatbot.sendMessage('Show my company sales report for this month', 'owner123');
  console.log('Bot:', res.message);
  console.log('Suggestions:', res.suggestedQueries);
}
```

## React Integration (Minimal)

```jsx
const API_BASE = 'http://localhost:5000/api/v1/chatbot';

async function sendMessage({ sessionId, message, companyId, userId }) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      user_id: userId,
      metadata: companyId ? { company_id: companyId } : undefined,
    }),
  });

  const data = await response.json();
  if (!data.success) throw new Error(data.error?.message || 'Chat request failed');

  return {
    sessionId: data.data.session_id,
    botMessage: data.data.message,
    suggestedQueries: data.data.suggested_queries || [],
  };
}
```

## Python Integration

```python
import requests

class ChatbotClient:
    def __init__(self, base_url='http://localhost:5000/api/v1/chatbot', company_id=None):
        self.base_url = base_url
        self.session_id = None
        self.company_id = company_id

    def send_message(self, message, user_id=None):
        payload = {
            'session_id': self.session_id,
            'message': message,
            'user_id': user_id,
        }
        if self.company_id is not None:
            payload['metadata'] = {'company_id': self.company_id}

        response = requests.post(f'{self.base_url}/chat', json=payload)
        data = response.json()

        if not data.get('success'):
            raise Exception(data.get('error', {}).get('message', 'Chat request failed'))

        self.session_id = data['data']['session_id']
        return data['data']['message'], data['data'].get('suggested_queries', [])
```

## cURL Example

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my company sales report for this month",
    "user_id": "owner123",
    "metadata": {
      "company_id": 1
    }
  }'
```

## Response Shape

```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "message": "assistant response",
    "timestamp": "2026-03-27T00:00:00Z",
    "suggested_queries": [
      "query 1",
      "query 2",
      "query 3",
      "query 4"
    ],
    "metadata": {
      "message_count": 4,
      "user_id": "owner123",
      "session_created": true,
      "company_id": 1
    }
  }
}
```
