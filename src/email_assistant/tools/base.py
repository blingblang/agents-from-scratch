from typing import Dict, List, Callable, Any
from langchain_core.tools import BaseTool

def get_tools(tool_names: List[str] | None = None, include_gmail: bool = False, include_zoho: bool = False) -> List[BaseTool]:
    """Get specified tools or all tools if tool_names is None.
    
    Args:
        tool_names: Optional list of tool names to include. If None, returns all tools.
        include_gmail: Whether to include Gmail tools. Defaults to False.
        include_zoho: Whether to include Zoho Inventory tools. Defaults to False.
        
    Returns:
        List of tool objects
    """
    # Import default tools
    from src.email_assistant.tools.default.email_tools import write_email, Done, Question
    from src.email_assistant.tools.default.calendar_tools import schedule_meeting, check_calendar_availability
    
    # Base tools dictionary
    all_tools = {
        "write_email": write_email,
        "Done": Done,
        "Question": Question,
        "schedule_meeting": schedule_meeting,
        "check_calendar_availability": check_calendar_availability,
    }
    
    # Add Gmail tools if requested
    if include_gmail:
        try:
            from src.email_assistant.tools.gmail.gmail_tools import (
                fetch_emails_tool,
                send_email_tool,
                check_calendar_tool,
                schedule_meeting_tool
            )
            
            all_tools.update({
                "fetch_emails_tool": fetch_emails_tool,
                "send_email_tool": send_email_tool,
                "check_calendar_tool": check_calendar_tool,
                "schedule_meeting_tool": schedule_meeting_tool,
            })
        except ImportError:
            # If Gmail tools aren't available, continue without them
            pass
    
    # Add Zoho Inventory tools if requested
    if include_zoho:
        try:
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
            
            all_tools.update({
                "fetch_inventory_tool": fetch_inventory_tool,
                "check_stock_levels_tool": check_stock_levels_tool,
                "get_sales_analytics_tool": get_sales_analytics_tool,
                "create_order_tool": create_order_tool,
                "update_inventory_tool": update_inventory_tool,
                "analyze_demand_patterns_tool": analyze_demand_patterns_tool,
                "forecast_demand_tool": forecast_demand_tool,
                "analyze_stockout_risk_tool": analyze_stockout_risk_tool,
                "generate_reorder_recommendations_tool": generate_reorder_recommendations_tool,
                "seasonal_demand_analysis_tool": seasonal_demand_analysis_tool,
                "find_suppliers_tool": find_suppliers_tool,
                "create_purchase_order_tool": create_purchase_order_tool,
                "check_order_status_tool": check_order_status_tool,
                "approve_purchase_order_tool": approve_purchase_order_tool,
                "cancel_purchase_order_tool": cancel_purchase_order_tool,
                "get_supplier_performance_tool": get_supplier_performance_tool,
                "bulk_restock_tool": bulk_restock_tool,
            })
        except ImportError:
            # If Zoho tools aren't available, continue without them
            pass
    
    if tool_names is None:
        return list(all_tools.values())
    
    return [all_tools[name] for name in tool_names if name in all_tools]

def get_tools_by_name(tools: List[BaseTool] | None = None) -> Dict[str, BaseTool]:
    """Get a dictionary of tools mapped by name."""
    if tools is None:
        tools = get_tools()
    
    return {tool.name: tool for tool in tools}
