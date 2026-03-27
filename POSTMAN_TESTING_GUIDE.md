# Postman Testing Guide

This guide helps anyone test the Bizwy Chatbot backend end-to-end using Postman.

## 1. Prerequisites

- Backend running locally:
  - `uvicorn app:app --host 0.0.0.0 --port 5000 --reload`
- Postman installed
- Valid `.env` configured (`OPENAI_*`, `PLATFORM_API_*`)

## 2. Create Postman Environment

Create an environment named `Bizwy Local` with these variables:

- `base_url` = `http://localhost:5000`
- `api_prefix` = `/api/v1/chatbot`
- `session_id` = ``
- `user_id` = `owner123`
- `company_id` = `1`

Use URL pattern:

- `{{base_url}}{{api_prefix}}/chat`

## 3. Recommended Collection Order

1. Health Check
2. First Chat Message (auto-create session)
3. Follow-up Chat Message (reuse session)
4. Sales Report Query
5. Stock Report Query
6. Get Session
7. Clear Session
8. Delete Session

## 4. Requests

## 4.1 Health Check

- Method: `GET`
- URL: `{{base_url}}{{api_prefix}}/health`
- Body: none

Expected:

- `success = true`
- `data.status = healthy`

## 4.2 First Chat Message (Auto Session)

- Method: `POST`
- URL: `{{base_url}}{{api_prefix}}/chat`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "message": "Show my company sales report for this month",
  "user_id": "{{user_id}}",
  "metadata": {
    "company_id": {{company_id}}
  }
}
```

Expected:

- `success = true`
- `data.session_id` is returned
- `data.message` is non-empty
- `data.suggested_queries` contains exactly 4 items
- `data.metadata.session_created = true`

## 4.3 Follow-up Chat Message (Reuse Session)

- Method: `POST`
- URL: `{{base_url}}{{api_prefix}}/chat`
- Body:

```json
{
  "session_id": "{{session_id}}",
  "message": "Show recent completed orders",
  "user_id": "{{user_id}}",
  "metadata": {
    "company_id": {{company_id}}
  }
}
```

Expected:

- `success = true`
- Same `session_id`
- `data.metadata.session_created = false`
- `data.suggested_queries` contains 4 items

## 4.4 Sales Report Query

- Method: `POST`
- URL: `{{base_url}}{{api_prefix}}/chat`
- Body:

```json
{
  "session_id": "{{session_id}}",
  "message": "Give me sales report from 2026-03-01 to 2026-03-31",
  "user_id": "{{user_id}}",
  "metadata": {
    "company_id": {{company_id}}
  }
}
```

Expected:

- `success = true`
- Natural-language report summary in `data.message`

## 4.5 Stock Report Query

- Method: `POST`
- URL: `{{base_url}}{{api_prefix}}/chat`
- Body:

```json
{
  "session_id": "{{session_id}}",
  "message": "Show low stock items with threshold 5",
  "user_id": "{{user_id}}",
  "metadata": {
    "company_id": {{company_id}}
  }
}
```

Expected:

- `success = true`
- Stock-focused answer
- 4 follow-up suggestions

## 4.6 Get Session

- Method: `GET`
- URL: `{{base_url}}{{api_prefix}}/sessions/{{session_id}}`

Expected:

- `success = true`
- `data.session_id` matches
- `data.message_count` is present

## 4.7 Clear Session

- Method: `POST`
- URL: `{{base_url}}{{api_prefix}}/sessions/{{session_id}}/clear`

Expected:

- `success = true`

## 4.8 Delete Session

- Method: `DELETE`
- URL: `{{base_url}}{{api_prefix}}/sessions/{{session_id}}`

Expected:

- `success = true`

## 5. Postman Tests (Copy/Paste)

Use this in the `Tests` tab for chat requests.

```javascript
pm.test("Status code is 200", function () {
  pm.response.to.have.status(200);
});

const json = pm.response.json();

pm.test("success is true", function () {
  pm.expect(json.success).to.eql(true);
});

pm.test("chat payload exists", function () {
  pm.expect(json.data).to.be.an("object");
  pm.expect(json.data.session_id).to.be.a("string");
  pm.expect(json.data.message).to.be.a("string");
});

pm.test("suggested_queries has 4 items", function () {
  pm.expect(json.data.suggested_queries).to.be.an("array");
  pm.expect(json.data.suggested_queries.length).to.eql(4);
});

if (json.data && json.data.session_id) {
  pm.environment.set("session_id", json.data.session_id);
}
```

## 6. Common Error Troubleshooting

## 6.1 `422 Validation failed` from report API

Cause:
- Invalid report filter values sent to platform API.

Action:
- Keep request simple first (message + `metadata.company_id`).
- Avoid forcing sort fields in user prompt.

## 6.2 `MISSING_COMPANY_ID`

Cause:
- Report query without tenant context.

Action:
- Send `metadata.company_id` in chat body.

## 6.3 `429 Too Many Requests`

Cause:
- Rate limit exceeded.

Action:
- Wait and retry, or increase `RATE_LIMIT_PER_MINUTE` in `.env` for test environment.

## 6.4 `500` on chat

Action:
- Check backend logs in terminal.
- Validate `.env` values for `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `PLATFORM_API_BASE_URL`, `PLATFORM_API_KEY`.

## 7. Smoke Test Checklist

- Health endpoint returns success
- First chat auto-creates session
- Follow-up chat reuses same session
- Report query works with `metadata.company_id`
- `suggested_queries` always returns 4 items
- Session clear and delete endpoints work

## 8. Recommended Shareable Artifacts

When sharing test results with QA/PM, include:

- Postman environment export
- Postman collection export
- Screenshots of 1 successful report query
- Screenshots of session create/reuse flow
- Any failed response payload + backend log snippet
