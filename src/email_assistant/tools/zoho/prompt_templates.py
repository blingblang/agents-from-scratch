"""Tool prompt templates for the Zoho Inventory sales monitor agent."""

# Zoho Inventory tool descriptions
ZOHO_TOOLS_PROMPT = """
1. fetch_inventory_tool(category, low_stock_only) - Fetch current inventory items, optionally filtered by category or low stock status
2. check_stock_levels_tool(item_name) - Check stock levels for specific items or get low stock alerts
3. get_sales_analytics_tool(period) - Get sales analytics and performance data for specified time period
4. create_order_tool(item_name, quantity, customer_email, notes) - Create a new sales order
5. update_inventory_tool(item_name, new_quantity, reason) - Update inventory quantity for an item
6. Question(content) - Ask the user any follow-up questions
7. Done - Task has been completed
"""

# Demand forecasting tool descriptions
DEMAND_FORECAST_TOOLS_PROMPT = """
1. analyze_demand_patterns_tool(item_name, period_days) - Analyze historical demand patterns for inventory items
2. forecast_demand_tool(item_name, forecast_days, method) - Forecast future demand for a specific item using various methods
3. analyze_stockout_risk_tool(minimum_days) - Analyze stockout risk across all inventory items  
4. generate_reorder_recommendations_tool(lead_time_days, safety_stock_days) - Generate intelligent reorder recommendations based on demand forecasts
5. seasonal_demand_analysis_tool(item_name) - Analyze seasonal demand patterns and provide seasonal forecasting insights
6. Question(content) - Ask the user any follow-up questions or clarifications
7. Done - Forecasting analysis has been completed
"""

# Restock and supplier management tool descriptions
RESTOCK_TOOLS_PROMPT = """
1. find_suppliers_tool(item_name, required_quantity) - Find available suppliers with pricing and lead times for specific items
2. create_purchase_order_tool(supplier_id, item_name, quantity, delivery_date, notes) - Create purchase orders with selected suppliers
3. check_order_status_tool(po_number) - Check status of purchase orders and track delivery progress
4. approve_purchase_order_tool(po_number, approval_notes) - Approve pending purchase orders and send to suppliers
5. cancel_purchase_order_tool(po_number, cancellation_reason) - Cancel purchase orders with appropriate notifications
6. get_supplier_performance_tool(supplier_id) - Get supplier performance metrics and ratings for decision making
7. bulk_restock_tool(restock_list, budget_limit) - Create bulk restock plans for multiple items with cost optimization
8. Question(content) - Ask the user for approval, clarification, or business input
9. Done - Procurement activities have been completed
""" 