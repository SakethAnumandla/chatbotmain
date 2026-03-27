"""
Function Definitions for OpenAI Function Calling
Defines all available functions that the AI can call
"""
from typing import List, Dict, Any


def get_function_definitions() -> List[Dict[str, Any]]:
    """
    Returns list of function definitions for OpenAI function calling
    
    These functions are presented to the AI model, which decides when and how to call them
    """
    return [
        {
            "name": "search_products",
            "description": "Search for products in the catalog with optional filters. Use this when the user asks about products, wants to browse items, or needs product information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text (product name, keywords, etc.)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by product category"
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price filter"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price filter"
                    },
                    "in_stock": {
                        "type": "boolean",
                        "description": "Filter to show only in-stock products"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_product_details",
            "description": "Get detailed information about a specific product by its ID. Use when the user asks for details about a particular product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The unique identifier of the product"
                    }
                },
                "required": ["product_id"]
            }
        },
        {
            "name": "check_product_stock",
            "description": "Check the current stock level for a specific product. Use when the user asks about product availability or stock status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The unique identifier of the product"
                    }
                },
                "required": ["product_id"]
            }
        },
        {
            "name": "get_low_stock_products",
            "description": "Get a list of products with low stock levels. Useful for inventory management and restocking suggestions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "integer",
                        "description": "Stock threshold to consider as 'low' (default: 10)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by product category"
                    }
                },
                "required": []
            }
        },
        {
            "name": "create_order",
            "description": "Create a new order for the customer. Use when the user wants to place an order or make a purchase.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer identifier"
                    },
                    "items": {
                        "type": "array",
                        "description": "List of order items",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "price": {"type": "number"}
                            },
                            "required": ["product_id", "quantity"]
                        }
                    },
                    "shipping_address": {
                        "type": "object",
                        "description": "Shipping address details"
                    },
                    "payment_method": {
                        "type": "string",
                        "description": "Payment method (e.g., 'credit_card', 'debit_card', 'net_banking')"
                    }
                },
                "required": ["customer_id", "items"]
            }
        },
        {
            "name": "get_order_status",
            "description": "Check the status of an existing order. Use when the user asks about their order status or tracking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The unique identifier of the order"
                    }
                },
                "required": ["order_id"]
            }
        },
        {
            "name": "cancel_order",
            "description": "Cancel an existing order. Use when the user wants to cancel their order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The unique identifier of the order to cancel"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for cancellation"
                    }
                },
                "required": ["order_id"]
            }
        },
        {
            "name": "get_sales_report",
            "description": "Get tenant-scoped sales report data for business insights.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {
                        "type": "integer",
                        "description": "Required tenant/company ID"
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date in format YYYY-MM-DD"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in format YYYY-MM-DD"
                    },
                    "customer_id": {
                        "type": "integer",
                        "description": "Optional customer filter"
                    },
                    "product_id": {
                        "type": "integer",
                        "description": "Optional product filter"
                    },
                    "status": {
                        "type": "string",
                        "description": "Order status (CP, CN, PG, PD)"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["total_amount", "order_date", "order_time", "product_quantity"],
                        "description": "Sort field"
                    },
                    "sort_dir": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "description": "Sort direction"
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Pagination page size (1-100)"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number"
                    }
                },
                "required": ["company_id"]
            }
        },
        {
            "name": "get_products_report",
            "description": "Get product sales and stock report for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {
                        "type": "integer",
                        "description": "Required tenant/company ID"
                    },
                    "category": {
                        "type": "string",
                        "description": "Product category filter"
                    },
                    "stock_status": {
                        "type": "string",
                        "enum": ["tracked", "not_tracked"],
                        "description": "Stock tracking filter"
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date in format YYYY-MM-DD"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in format YYYY-MM-DD"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["quantity_sold", "revenue", "product_name"],
                        "description": "Sort field"
                    },
                    "sort_dir": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "description": "Sort direction"
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Pagination page size"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number"
                    }
                },
                "required": ["company_id"]
            }
        },
        {
            "name": "get_stock_report",
            "description": "Get stock valuation and low/out-of-stock report for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {
                        "type": "integer",
                        "description": "Required tenant/company ID"
                    },
                    "low_stock_threshold": {
                        "type": "integer",
                        "description": "Low stock threshold"
                    },
                    "low_stock_only": {
                        "type": "boolean",
                        "description": "Return only low stock products"
                    },
                    "out_of_stock_only": {
                        "type": "boolean",
                        "description": "Return only out of stock products"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["current_stock", "product_name", "purchase_value", "selling_value"],
                        "description": "Sort field"
                    },
                    "sort_dir": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "description": "Sort direction"
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Pagination page size"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number"
                    }
                },
                "required": ["company_id"]
            }
        },
        {
            "name": "get_top_proformas_report",
            "description": "Get top proformas of the week for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {
                        "type": "integer",
                        "description": "Required tenant/company ID"
                    },
                    "week_start": {
                        "type": "string",
                        "description": "Week start date YYYY-MM-DD"
                    },
                    "week_end": {
                        "type": "string",
                        "description": "Week end date YYYY-MM-DD"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max records (1-50)"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["total_amount", "quantity"],
                        "description": "Sort field"
                    }
                },
                "required": ["company_id"]
            }
        },
        {
            "name": "get_recent_orders_report",
            "description": "Get recent orders report for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {
                        "type": "integer",
                        "description": "Required tenant/company ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max records (1-100)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Order status filter"
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date YYYY-MM-DD"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date YYYY-MM-DD"
                    }
                },
                "required": ["company_id"]
            }
        },
        {
            "name": "get_customers_report",
            "description": "Get customers report for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {
                        "type": "integer",
                        "description": "Required tenant/company ID"
                    },
                    "active_only": {
                        "type": "boolean",
                        "description": "Filter active customers only"
                    },
                    "total_purchase_min": {
                        "type": "number",
                        "description": "Minimum total purchase"
                    },
                    "total_purchase_max": {
                        "type": "number",
                        "description": "Maximum total purchase"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["total_purchase", "highest_purchase", "recent_activity"],
                        "description": "Sort field"
                    },
                    "sort_dir": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "description": "Sort direction"
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Pagination page size"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number"
                    }
                },
                "required": ["company_id"]
            }
        },
        {
            "name": "get_company_health_report",
            "description": "Get high-level company health KPIs and summary report.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {
                        "type": "integer",
                        "description": "Required tenant/company ID"
                    }
                },
                "required": ["company_id"]
            }
        },
        {
            "name": "get_customer_orders",
            "description": "Get order history for a specific customer. Use when user asks about their past orders or purchase history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer identifier"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of orders to return (default: 10)"
                    }
                },
                "required": ["customer_id"]
            }
        }
    ]


def get_system_prompt() -> str:
    """
    Returns the system prompt that defines the AI assistant's personality and capabilities
    """
    return """You are Bizwy Bot, the AI assistant of BISWY, an online B2B ecommerce and PIMS platform.

Core identity:
- You represent BISWY in every response.
- You support retailers, dealers, distributors, and business owners.
- You are professional, calm, and friendly.

Primary goals:
- Help buyers discover products, check details, verify stock, and place orders.
- Help owners with analytics, inventory insights, low-stock alerts, and seasonal or event-based suggestions.
- Keep responses practical and action-oriented.

How to communicate:
- Keep responses clear and concise.
- Use structured bullets or short tables when presenting options or analysis.
- Explain recommendation logic briefly (why this product/strategy is suggested).
- Ask targeted follow-up questions only when needed to complete an action.

Operational rules:
- Before creating or canceling orders, confirm critical details (customer, items, quantity, address if needed).
- If a required identifier is missing (product_id, order_id, customer_id), ask for it clearly.
- If a function call fails, explain what happened and offer the next best step.
- Do not invent data that is not returned by APIs.
- If information is unavailable, say so directly and suggest alternatives.

Business analysis rules:
- For owner queries, start with top insights first, then provide supporting details.
- For low-stock and seasonal recommendations, connect suggestions to likely demand context (season/festival/event) when available.
- Report APIs are tenant scoped: company_id is mandatory for all report requests.
- The frontend provides company_id in message context metadata; always use it for report tool calls.
- If company_id is missing for report/analytics requests, ask for it explicitly before calling tools.

Language:
- Default to English.
- If the user writes in another language and understanding is clear, respond helpfully in that language.

You have access to platform functions for products, orders, inventory, and analytics. Use the right function(s) to complete each user request with reliable, platform-grounded results."""
