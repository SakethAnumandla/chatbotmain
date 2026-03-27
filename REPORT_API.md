# Report & Analytics API

Multi-tenant report endpoints. All require `company_id` (integer) for tenant scope.

**Base URL:** `GET /api/reports/...`

**Response shape (all endpoints):**
```json
{
  "success": true,
  "message": "Report fetched successfully",
  "data": {},
  "meta": {
    "pagination": {},
    "filters": {},
    "summary": {}
  }
}
```

---

## 1. Sales Report

**Endpoint:** `GET /api/reports/sales`

**Query parameters:**

| Parameter    | Type   | Required | Description |
|-------------|--------|----------|-------------|
| company_id  | int    | Yes      | Tenant ID   |
| from_date   | date   | No       | Y-m-d       |
| to_date     | date   | No       | Y-m-d, >= from_date |
| customer_id | int    | No       | Filter by customer |
| product_id  | int    | No       | Filter orders containing this product |
| status      | string/array | No | Order status: CP, CN, PG, PD |
| sort_by     | string | No       | total_amount, order_date, order_time, product_quantity (default: order_date) |
| sort_dir    | string | No       | asc, desc (default: desc) |
| per_page    | int    | No       | 1–100 (default: 15) |
| page        | int    | No       | Page number |

**Example request:**
```bash
curl -X GET "https://business.bizwy.in/v2/notification/api/v1/reports/sales?company_id=1&from_date=2025-01-01&to_date=2025-02-23&sort_by=total_amount&sort_dir=desc&per_page=10"
```

**Example response:**
```json
{
  "success": true,
  "message": "Report fetched successfully",
  "data": [
    {
      "order_id": "ORD-001",
      "order_date": "2025-02-20",
      "order_time": "14:30:00",
      "order_status": "CP",
      "customer_id": 10,
      "customer_name": "John Doe",
      "total_amount": 2500.00,
      "tax_amount": 380.00,
      "discount_amount": 100.00,
      "net_amount": 2020.00,
      "quantity": 5
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "last_page": 3,
      "per_page": 10,
      "total": 28,
      "from": 1,
      "to": 10
    },
    "filters": { "company_id": 1, "from_date": "2025-01-01", "to_date": "2025-02-23" },
    "summary": {
      "total_sales_amount": 125000.50,
      "total_tax": 18000.00,
      "total_discount": 5000.00,
      "net_revenue": 102000.50,
      "total_orders": 28
    }
  }
}
```

---

## 2. Product Report

**Endpoint:** `GET /api/reports/products`

**Query parameters:** company_id (required), category, stock_status (tracked|not_tracked), from_date, to_date, sort_by (quantity_sold|revenue|product_name), sort_dir, per_page, page.

**Example request:**
```bash
curl -X GET "https://business.bizwy.in/v2/notification/api/v1/reports/products?company_id=1&sort_by=revenue&sort_dir=desc&per_page=15"
```

**Example response (data item):**
```json
{
  "product_id": 101,
  "product_name": "Widget A",
  "product_code": "WGT-A",
  "quantity_sold": 150,
  "revenue": 45000.00,
  "current_stock": 25,
  "product_status": "A"
}
```

---

## 3. Stock Report

**Endpoint:** `GET /api/reports/stock`

**Query parameters:** company_id (required), low_stock_threshold (int), low_stock_only (bool), out_of_stock_only (bool), sort_by (current_stock|product_name|purchase_value|selling_value), sort_dir, per_page, page.

**Example request:**
```bash
curl -X GET "https://business.bizwy.in/v2/notification/api/v1/reports/stock?company_id=1&low_stock_threshold=5&low_stock_only=0"
```

**Example response (data item):**
```json
{
  "product_id": 101,
  "product_name": "Widget A",
  "product_code": "WGT-A",
  "current_stock": 3,
  "purchase_value": 450.00,
  "selling_value": 600.00,
  "is_low_stock": true,
  "is_out_of_stock": false
}
```

**meta.summary:** total_stock_valuation_purchase, total_stock_valuation_selling, products_count.

---

## 4. Top Proformas of the Week

**Endpoint:** `GET /api/reports/top-proformas`

**Query parameters:** company_id (required), week_start (date), week_end (date), limit (1–50, default 10), sort_by (total_amount|quantity).

**Example request:**
```bash
curl -X GET "https://business.bizwy.in/v2/notification/api/v1/reports/top-proformas?company_id=1&limit=5&sort_by=total_amount"
```

**Example response (data item):**
```json
{
  "proforma_no": "PRO-2025-001",
  "proforma_id": 42,
  "total_amount": 15000.00,
  "quantity": 20,
  "proforma_status": "approved",
  "proforma_date": "2025-02-20 10:00:00",
  "customer": {
    "id": 10,
    "name": "Jane Smith",
    "mobile": "9876543210"
  }
}
```

---

## 5. Recent Orders

**Endpoint:** `GET /api/reports/recent-orders`

**Query parameters:** company_id (required), limit (1–100, default 20), status, from_date, to_date.

**Example request:**
```bash
curl -X GET "https://business.bizwy.in/v2/notification/api/v1/reports/recent-orders?company_id=1&limit=10&status=CP"
```

**Example response (data item):**
```json
{
  "order_id": "ORD-002",
  "order_date": "2025-02-22",
  "order_time": "16:45:00",
  "order_status": "CP",
  "total": 3200.00,
  "customer": { "id": 12, "name": "Bob Wilson", "mobile": "9123456789" },
  "payment_mode": "Card"
}
```

---

## 6. Customers List

**Endpoint:** `GET /api/reports/customers`

**Query parameters:** company_id (required), active_only (bool), total_purchase_min, total_purchase_max, sort_by (total_purchase|highest_purchase|recent_activity), sort_dir, per_page, page.

**Example request:**
```bash
curl -X GET "https://business.bizwy.in/v2/notification/api/v1/reports/customers?company_id=1&sort_by=total_purchase&sort_dir=desc&per_page=20"
```

**Example response (data item):**
```json
{
  "customer_id": 10,
  "first_name": "John",
  "last_name": "Doe",
  "user_status": "A",
  "mobile": "9876543210",
  "total_orders": 15,
  "total_purchase": 85000.50
}
```

---

## 7. Company Health

**Endpoint:** `GET /api/reports/company-health`

**Query parameters:** company_id (required).

**Example request:**
```bash
curl -X GET "https://business.bizwy.in/v2/notification/api/v1/reports/company-health?company_id=1"
```

**Example response (data = summary):**
```json
{
  "success": true,
  "message": "Report fetched successfully",
  "data": {
    "total_revenue_current_month": 125000.50,
    "revenue_growth_percent": 12.5,
    "total_orders_current_month": 85,
    "average_order_value": 1470.59,
    "outstanding_payments": 25000.00,
    "stock_valuation": 180000.00,
    "top_selling_product": "Widget A",
    "top_selling_product_id": 101,
    "top_customer": "Jane Smith",
    "top_customer_id": 15
  },
  "meta": { "summary": { ... } }
}
```

---

## Caching

- Company health report uses Laravel cache with tenant-specific keys (`report_company_{id}_health`).
- TTL is set in `config/reports.php` and can be overridden by `REPORTS_CACHE_TTL` (seconds). Set to `0` to disable.

## Validation

- All endpoints use Form Request classes; invalid input returns `422` with `errors` object.
- `company_id` is required on every request. Sort and filter values are whitelisted to avoid SQL injection.
