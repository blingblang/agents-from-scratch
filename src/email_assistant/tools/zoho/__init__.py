from src.email_assistant.tools.zoho.zoho_tools import (
    fetch_inventory_tool,
    check_stock_levels_tool,
    get_sales_analytics_tool,
    create_order_tool,
    update_inventory_tool
)

from src.email_assistant.tools.zoho.demand_forecast_tools import (
    analyze_demand_patterns_tool,
    forecast_demand_tool,
    analyze_stockout_risk_tool,
    generate_reorder_recommendations_tool,
    seasonal_demand_analysis_tool
)

from src.email_assistant.tools.zoho.restock_tools import (
    find_suppliers_tool,
    create_purchase_order_tool,
    check_order_status_tool,
    approve_purchase_order_tool,
    cancel_purchase_order_tool,
    get_supplier_performance_tool,
    bulk_restock_tool
)

__all__ = [
    # Original Zoho inventory tools
    "fetch_inventory_tool",
    "check_stock_levels_tool", 
    "get_sales_analytics_tool",
    "create_order_tool",
    "update_inventory_tool",
    # Demand forecasting tools
    "analyze_demand_patterns_tool",
    "forecast_demand_tool",
    "analyze_stockout_risk_tool",
    "generate_reorder_recommendations_tool",
    "seasonal_demand_analysis_tool",
    # Restock and supplier management tools
    "find_suppliers_tool",
    "create_purchase_order_tool",
    "check_order_status_tool",
    "approve_purchase_order_tool",
    "cancel_purchase_order_tool",
    "get_supplier_performance_tool",
    "bulk_restock_tool"
] 