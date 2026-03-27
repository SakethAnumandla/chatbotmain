"""
OpenAI Service
Handles interactions with OpenAI API including function calling orchestration
"""
import json
from typing import Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from config import settings
from app.models.chat import ConversationContext, MessageRole, ChatMessage
from app.services.function_definitions import get_function_definitions, get_system_prompt
from app.infrastructure.api.platform_client import PlatformAPIClient
from app.utils.logger import get_logger

logger = get_logger(__name__)

REPORT_FUNCTIONS = {
    "get_sales_report",
    "get_products_report",
    "get_stock_report",
    "get_top_proformas_report",
    "get_recent_orders_report",
    "get_customers_report",
    "get_company_health_report",
}


class OpenAIService:
    """Service for OpenAI API interactions with function calling"""
    
    def __init__(self, platform_client: PlatformAPIClient):
        """
        Initialize OpenAI service
        
        Args:
            platform_client: Platform API client for function execution
        """
        self.platform_client = platform_client
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        self.model = settings.openai_model
        self.functions = get_function_definitions()
        self.tools = [{"type": "function", "function": fn} for fn in self.functions]
        logger.info(f"OpenAI service initialized with model: {self.model}")

    async def _create_completion(self, messages: list[dict[str, Any]]) -> Tuple[Any, str]:
        """Create a completion using tools-first, then fallback to legacy functions mode."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000,
            )
            return response, "tools"
        except Exception as tool_error:
            logger.warning(f"Tools mode unavailable, falling back to legacy functions mode: {tool_error}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=self.functions,
                function_call="auto",
                temperature=0.7,
                max_tokens=1000,
            )
            return response, "functions"
    
    async def chat(
        self,
        context: ConversationContext,
        user_message: str
    ) -> str:
        """
        Process a chat message and return AI response
        
        Args:
            context: Conversation context with history
            user_message: New message from user
            
        Returns:
            AI assistant's response
        """
        # Add user message to context
        context.add_message(MessageRole.USER, user_message)
        
        # Ensure system prompt is present
        if not any(msg.role == MessageRole.SYSTEM for msg in context.messages):
            context.messages.insert(
                0,
                ChatMessage(role=MessageRole.SYSTEM, content=get_system_prompt())
            )
        
        # Manage context window size
        context.clear_old_messages(keep_last=20)
        
        # Get messages in OpenAI format with metadata-derived execution context.
        messages = self._build_messages_for_api(context)
        
        try:
            # Initial API call
            response, mode = await self._create_completion(messages)
            
            assistant_message = response.choices[0].message
            
            # Handle function calling loop
            max_iterations = 5  # Prevent infinite loops
            iteration = 0
            
            while iteration < max_iterations:
                tool_calls = getattr(assistant_message, "tool_calls", None) or []
                function_call = getattr(assistant_message, "function_call", None)

                if not tool_calls and not function_call:
                    break

                iteration += 1
                if tool_calls:
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        raw_args = tool_call.function.arguments or "{}"
                        function_args = json.loads(raw_args)

                        logger.info(f"Function call: {function_name} with args: {function_args}")

                        function_result = await self._execute_function(function_name, function_args, context)

                        # Persist call/result in conversation context
                        context.add_message(
                            MessageRole.ASSISTANT,
                            "",
                            function_call={
                                "name": function_name,
                                "arguments": json.dumps(function_args)
                            }
                        )
                        context.add_message(
                            MessageRole.FUNCTION,
                            json.dumps(function_result),
                            name=function_name
                        )

                        # Append tool result for next model turn
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": json.dumps(function_result),
                            }
                        )
                elif function_call:
                    function_name = function_call.name
                    raw_args = function_call.arguments or "{}"
                    function_args = json.loads(raw_args)

                    logger.info(f"Function call: {function_name} with args: {function_args}")

                    function_result = await self._execute_function(function_name, function_args, context)

                    context.add_message(
                        MessageRole.ASSISTANT,
                        "",
                        function_call={
                            "name": function_name,
                            "arguments": json.dumps(function_args)
                        }
                    )
                    context.add_message(
                        MessageRole.FUNCTION,
                        json.dumps(function_result),
                        name=function_name
                    )

                    # Legacy function mode follow-up messages
                    messages.append(
                        {
                            "role": "assistant",
                            "content": assistant_message.content or "",
                            "function_call": {
                                "name": function_name,
                                "arguments": json.dumps(function_args),
                            },
                        }
                    )
                    messages.append(
                        {
                            "role": "function",
                            "name": function_name,
                            "content": json.dumps(function_result),
                        }
                    )

                # Get next response from AI
                if mode == "tools":
                    response, mode = await self._create_completion(messages)
                else:
                    response, mode = await self._create_completion(messages)
                
                assistant_message = response.choices[0].message
            
            # Get final response
            final_response = assistant_message.content or "I apologize, but I couldn't generate a response."
            
            # Add assistant's final message to context
            context.add_message(MessageRole.ASSISTANT, final_response)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error in OpenAI chat: {e}", exc_info=True)
            error_message = "I apologize, but I encountered an error processing your request. Please try again."
            context.add_message(MessageRole.ASSISTANT, error_message)
            return error_message

    def _build_messages_for_api(self, context: ConversationContext) -> list[dict[str, Any]]:
        """
        Build OpenAI messages and inject tenant context hints from metadata.

        This ensures report calls can use company_id provided by frontend metadata
        without repeatedly asking the user for it.
        """
        messages = context.get_messages_for_api()

        company_id = context.metadata.get("company_id")
        if company_id is not None:
            system_hint = {
                "role": "system",
                "content": (
                    f"Runtime context: company_id={company_id}. "
                    "Use this company_id for all report tool calls by default. "
                    "Do not ask for company_id again unless user wants to switch company."
                ),
            }

            # Keep system messages at the top for deterministic behavior.
            insert_at = 1 if messages and messages[0].get("role") == "system" else 0
            messages.insert(insert_at, system_hint)

        return messages
    
    async def _execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        context: ConversationContext,
    ) -> Dict[str, Any]:
        """
        Execute a function call by routing to appropriate platform API
        
        Args:
            function_name: Name of the function to execute
            arguments: Function arguments
            
        Returns:
            Function execution result
        """
        try:
            if function_name in REPORT_FUNCTIONS and "company_id" not in arguments:
                company_id = context.metadata.get("company_id")
                if company_id is not None:
                    arguments["company_id"] = company_id

            if function_name in REPORT_FUNCTIONS and "company_id" not in arguments:
                logger.warning(
                    "Blocked report function '%s' due to missing company_id in function args and session metadata",
                    function_name,
                )
                return {
                    "success": False,
                    "error": "MISSING_COMPANY_ID",
                    "message": "company_id is required for report APIs. Frontend must send metadata.company_id in chat requests."
                }

            # Route to appropriate API method
            if function_name == "search_products":
                result = await self.platform_client.search_products(**arguments)
            
            elif function_name == "get_product_details":
                result = await self.platform_client.get_product_details(arguments["product_id"])
            
            elif function_name == "check_product_stock":
                result = await self.platform_client.get_product_stock(arguments["product_id"])
            
            elif function_name == "get_low_stock_products":
                result = await self.platform_client.get_low_stock_products(**arguments)
            
            elif function_name == "create_order":
                result = await self.platform_client.create_order(arguments)
            
            elif function_name == "get_order_status":
                result = await self.platform_client.get_order_status(arguments["order_id"])
            
            elif function_name == "cancel_order":
                result = await self.platform_client.cancel_order(**arguments)
            
            elif function_name == "get_sales_report":
                result = await self.platform_client.get_sales_report(**arguments)

            elif function_name == "get_products_report":
                result = await self.platform_client.get_products_report(**arguments)

            elif function_name == "get_stock_report":
                result = await self.platform_client.get_stock_report(**arguments)

            elif function_name == "get_top_proformas_report":
                result = await self.platform_client.get_top_proformas_report(**arguments)

            elif function_name == "get_recent_orders_report":
                result = await self.platform_client.get_recent_orders_report(**arguments)

            elif function_name == "get_customers_report":
                result = await self.platform_client.get_customers_report(**arguments)

            elif function_name == "get_company_health_report":
                result = await self.platform_client.get_company_health_report(**arguments)

            elif function_name == "get_sales_analytics":
                result = await self.platform_client.get_sales_analytics(**arguments)
            
            elif function_name == "get_product_recommendations":
                result = await self.platform_client.get_product_recommendations(**arguments)
            
            elif function_name == "get_inventory_analysis":
                result = await self.platform_client.get_inventory_analysis()
            
            elif function_name == "get_customer_orders":
                result = await self.platform_client.get_customer_orders(**arguments)
            
            else:
                result = {"error": f"Unknown function: {function_name}"}
                logger.warning(f"Unknown function called: {function_name}")
            
            logger.info(f"Function {function_name} executed successfully")
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute the requested operation"
            }
