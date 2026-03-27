# API Details Required From Platform Team

Please fill this file and share it back. I will then wire the chatbot APIs exactly to your platform contracts without assumptions.

## Global API Information

- Base URL:
- Authentication type: (Bearer token / API key / custom)
- Auth header format:
- Token/API key refresh flow (if any):
- Standard response envelope format:
- Standard error format:
- Rate limits:
- Timeout expectations:
- Idempotency support (if any):

## Endpoint Template (Use for each API)

Copy this block for every endpoint:

```text
API Name:
Method:
Path:
Purpose:
Authentication Required: (Yes/No)
Headers Required:
Query Params:
Path Params:
Request Body Schema:
Success Response Schema:
Error Response Schema:
Business Rules:
Validation Rules:
Example Request:
Example Response:
```

## Products APIs

1. Search Products
- Method/Path:
- Query filters supported: (query, category, min_price, max_price, in_stock, limit, offset, others)
- Response fields per product:

2. Product Details
- Method/Path:
- Required identifier:
- Response fields:

3. Product Stock
- Method/Path:
- Is stock warehouse-wise?:
- Response fields:

4. Low Stock Products
- Method/Path:
- Threshold logic:
- Category filter supported?:

## Orders APIs

1. Create Order
- Method/Path:
- Required fields: (customer_id, items, quantity, price, shipping, payment, etc.)
- Confirmation flow needed before order create?:

2. Order Status
- Method/Path:
- Valid order status values:

3. Update Order (if supported)
- Method/Path:
- Updatable fields:

4. Cancel Order
- Method/Path:
- Cancellation constraints:
- Required reason?:

## Analytics APIs

1. Sales Analytics
- Method/Path:
- Date range format:
- Group by values:
- Key metrics returned:

2. Product Recommendations
- Method/Path:
- Inputs supported: (context, season, event, limit)
- Recommendation logic source:

3. Inventory Analysis
- Method/Path:
- Returned metrics:

## Customers APIs

1. Customer Info
- Method/Path:
- Fields returned:

2. Customer Orders
- Method/Path:
- Filters supported:

## Session and Identity Mapping

- How should chatbot map platform user to `user_id`?
- Should tenant/company ID be passed for B2B isolation?
- Should each request include auth token of logged-in platform user?
- Any role-based access constraints (retailer/dealer/distributor/owner)?

## Seasonal/Festival/Event Input

- Will your platform provide current season/event via API, or should it come from user query only?
- If API-based, share endpoint and response contract.

## Notes

- Any endpoints that must never be called by chatbot:
- Any compliance/audit requirements:
- Any additional business constraints:
