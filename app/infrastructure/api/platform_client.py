"""
Platform API Client
Handles all communication with the PIMS/Ecommerce platform APIs
"""
from typing import Dict, Any, Optional, List, Union
import httpx
from config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PlatformAPIClient:
    """HTTP client for platform API integration"""
    
    def __init__(self):
        """Initialize the API client with configuration"""
        self.base_url = settings.platform_api_base_url.rstrip('/')
        self.api_key = settings.platform_api_key
        self.timeout = settings.platform_api_timeout
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Bizwy-Chatbot/1.0"
            }
        )
        logger.info(f"Platform API client initialized for {self.base_url}")
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the platform API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json: Request body
            
        Returns:
            API response as dictionary
        """
        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            raise
    
    # ============== Product APIs ==============
    
    async def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: Optional[bool] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for products with filters
        
        Args:
            query: Search query
            category: Product category
            min_price: Minimum price filter
            max_price: Maximum price filter
            in_stock: Filter by stock availability
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            Product search results
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if query:
            params["q"] = query
        if category:
            params["category"] = category
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if in_stock is not None:
            params["in_stock"] = in_stock
        
        logger.info(f"Searching products with params: {params}")
        return await self._request("GET", "/products", params=params)
    
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific product
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product details
        """
        logger.info(f"Fetching product details for ID: {product_id}")
        return await self._request("GET", f"/products/{product_id}")
    
    async def get_product_stock(self, product_id: str) -> Dict[str, Any]:
        """
        Get stock information for a product
        
        Args:
            product_id: Product identifier
            
        Returns:
            Stock information
        """
        logger.info(f"Fetching stock info for product ID: {product_id}")
        return await self._request("GET", f"/products/{product_id}/stock")
    
    async def get_low_stock_products(
        self,
        threshold: int = 10,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get products with low stock levels
        
        Args:
            threshold: Stock threshold
            category: Optional category filter
            
        Returns:
            List of low stock products
        """
        params = {"threshold": threshold}
        if category:
            params["category"] = category
        
        logger.info(f"Fetching low stock products with threshold: {threshold}")
        return await self._request("GET", "/products/low-stock", params=params)
    
    # ============== Order APIs ==============
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new order
        
        Args:
            order_data: Order details including items, customer info, etc.
            
        Returns:
            Created order details
        """
        logger.info(f"Creating order: {order_data}")
        return await self._request("POST", "/orders", json=order_data)
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get status of an existing order
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order status details
        """
        logger.info(f"Fetching order status for ID: {order_id}")
        return await self._request("GET", f"/orders/{order_id}")
    
    async def update_order(self, order_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing order
        
        Args:
            order_id: Order identifier
            updates: Fields to update
            
        Returns:
            Updated order details
        """
        logger.info(f"Updating order {order_id} with: {updates}")
        return await self._request("PUT", f"/orders/{order_id}", json=updates)
    
    async def cancel_order(self, order_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel an existing order
        
        Args:
            order_id: Order identifier
            reason: Cancellation reason
            
        Returns:
            Cancellation confirmation
        """
        data = {"reason": reason} if reason else {}
        logger.info(f"Cancelling order: {order_id}")
        return await self._request("POST", f"/orders/{order_id}/cancel", json=data)
    
    # ============== Analytics APIs ==============

    async def get_sales_report(
        self,
        company_id: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        customer_id: Optional[int] = None,
        product_id: Optional[int] = None,
        status: Optional[Union[str, List[str]]] = None,
        sort_by: Optional[str] = None,
        sort_dir: Optional[str] = None,
        per_page: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get sales report from /reports/sales"""
        allowed_sort_fields = {"total_amount", "order_date", "order_time", "product_quantity"}
        sort_aliases = {
            "date": "order_date",
            "time": "order_time",
            "amount": "total_amount",
            "quantity": "product_quantity",
        }

        params: Dict[str, Any] = {"company_id": company_id}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        if customer_id is not None:
            params["customer_id"] = customer_id
        if product_id is not None:
            params["product_id"] = product_id
        if status:
            params["status"] = ",".join(status) if isinstance(status, list) else status
        if sort_by:
            normalized_sort_by = sort_aliases.get(sort_by.strip().lower(), sort_by.strip().lower())
            if normalized_sort_by in allowed_sort_fields:
                params["sort_by"] = normalized_sort_by
            else:
                logger.warning(
                    "Ignoring unsupported sales report sort_by=%s. Allowed values: %s",
                    sort_by,
                    sorted(allowed_sort_fields),
                )
        if sort_dir:
            normalized_sort_dir = sort_dir.strip().lower()
            if normalized_sort_dir in {"asc", "desc"}:
                params["sort_dir"] = normalized_sort_dir
            else:
                logger.warning("Ignoring unsupported sales report sort_dir=%s", sort_dir)
        if per_page is not None:
            params["per_page"] = per_page
        if page is not None:
            params["page"] = page

        logger.info(f"Fetching sales report for company_id={company_id}")
        return await self._request("GET", "/reports/sales", params=params)

    async def get_products_report(
        self,
        company_id: int,
        category: Optional[str] = None,
        stock_status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_dir: Optional[str] = None,
        per_page: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get product report from /reports/products"""
        params: Dict[str, Any] = {"company_id": company_id}
        if category:
            params["category"] = category
        if stock_status:
            params["stock_status"] = stock_status
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        if sort_by:
            params["sort_by"] = sort_by
        if sort_dir:
            params["sort_dir"] = sort_dir
        if per_page is not None:
            params["per_page"] = per_page
        if page is not None:
            params["page"] = page

        logger.info(f"Fetching products report for company_id={company_id}")
        return await self._request("GET", "/reports/products", params=params)

    async def get_stock_report(
        self,
        company_id: int,
        low_stock_threshold: Optional[int] = None,
        low_stock_only: Optional[bool] = None,
        out_of_stock_only: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_dir: Optional[str] = None,
        per_page: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get stock report from /reports/stock"""
        params: Dict[str, Any] = {"company_id": company_id}
        if low_stock_threshold is not None:
            params["low_stock_threshold"] = low_stock_threshold
        if low_stock_only is not None:
            params["low_stock_only"] = int(low_stock_only)
        if out_of_stock_only is not None:
            params["out_of_stock_only"] = int(out_of_stock_only)
        if sort_by:
            params["sort_by"] = sort_by
        if sort_dir:
            params["sort_dir"] = sort_dir
        if per_page is not None:
            params["per_page"] = per_page
        if page is not None:
            params["page"] = page

        logger.info(f"Fetching stock report for company_id={company_id}")
        return await self._request("GET", "/reports/stock", params=params)

    async def get_top_proformas_report(
        self,
        company_id: int,
        week_start: Optional[str] = None,
        week_end: Optional[str] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get top proformas report from /reports/top-proformas"""
        params: Dict[str, Any] = {"company_id": company_id}
        if week_start:
            params["week_start"] = week_start
        if week_end:
            params["week_end"] = week_end
        if limit is not None:
            params["limit"] = limit
        if sort_by:
            params["sort_by"] = sort_by

        logger.info(f"Fetching top proformas report for company_id={company_id}")
        return await self._request("GET", "/reports/top-proformas", params=params)

    async def get_recent_orders_report(
        self,
        company_id: int,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get recent orders report from /reports/recent-orders"""
        params: Dict[str, Any] = {"company_id": company_id}
        if limit is not None:
            params["limit"] = limit
        if status:
            params["status"] = status
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date

        logger.info(f"Fetching recent orders report for company_id={company_id}")
        return await self._request("GET", "/reports/recent-orders", params=params)

    async def get_customers_report(
        self,
        company_id: int,
        active_only: Optional[bool] = None,
        total_purchase_min: Optional[float] = None,
        total_purchase_max: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_dir: Optional[str] = None,
        per_page: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get customers report from /reports/customers"""
        params: Dict[str, Any] = {"company_id": company_id}
        if active_only is not None:
            params["active_only"] = int(active_only)
        if total_purchase_min is not None:
            params["total_purchase_min"] = total_purchase_min
        if total_purchase_max is not None:
            params["total_purchase_max"] = total_purchase_max
        if sort_by:
            params["sort_by"] = sort_by
        if sort_dir:
            params["sort_dir"] = sort_dir
        if per_page is not None:
            params["per_page"] = per_page
        if page is not None:
            params["page"] = page

        logger.info(f"Fetching customers report for company_id={company_id}")
        return await self._request("GET", "/reports/customers", params=params)

    async def get_company_health_report(self, company_id: int) -> Dict[str, Any]:
        """Get company health report from /reports/company-health"""
        logger.info(f"Fetching company health report for company_id={company_id}")
        return await self._request("GET", "/reports/company-health", params={"company_id": company_id})
    
    async def get_sales_analytics(
        self,
        company_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """
        Get sales analytics data
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            group_by: Grouping period (day, week, month)
            
        Returns:
            Sales analytics data
        """
        # Backward-compatible wrapper to report API contract.
        return await self.get_sales_report(
            company_id=company_id,
            from_date=start_date,
            to_date=end_date,
        )
    
    async def get_product_recommendations(
        self,
        context: str,
        season: Optional[str] = None,
        event: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get product recommendations based on context
        
        Args:
            context: Context for recommendations (e.g., 'low_stock', 'trending')
            season: Current season
            event: Upcoming event/festival
            limit: Number of recommendations
            
        Returns:
            Product recommendations
        """
        params = {
            "context": context,
            "limit": limit
        }
        if season:
            params["season"] = season
        if event:
            params["event"] = event
        
        logger.info(f"Fetching product recommendations: {params}")
        return await self._request("GET", "/analytics/recommendations", params=params)
    
    async def get_inventory_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive inventory analysis
        
        Returns:
            Inventory analysis data
        """
        logger.info("Inventory analysis endpoint requires company_id via report APIs")
        return {
            "success": False,
            "message": "company_id is required. Use get_stock_report or get_company_health_report."
        }
    
    # ============== Customer APIs ==============
    
    async def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """
        Get customer information
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Customer details
        """
        logger.info(f"Fetching customer info for ID: {customer_id}")
        return await self._request("GET", f"/customers/{customer_id}")
    
    async def get_customer_orders(
        self,
        customer_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get order history for a customer
        
        Args:
            customer_id: Customer identifier
            limit: Maximum number of orders
            
        Returns:
            Customer order history
        """
        params = {"limit": limit}
        logger.info(f"Fetching orders for customer: {customer_id}")
        return await self._request("GET", f"/customers/{customer_id}/orders", params=params)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        logger.info("Platform API client closed")
