"""Utility functions for the inventory monitoring sales agent."""

from typing import Dict, Any, Tuple
import json

def parse_inventory_trigger(trigger_data: Dict[str, Any]) -> Tuple[str, str, str, Dict[str, Any]]:
    """Parse inventory trigger data into components.
    
    Args:
        trigger_data: Dictionary containing trigger information
        
    Returns:
        Tuple of (trigger_type, triggered_by, priority, details)
    """
    trigger_type = trigger_data.get("trigger_type", "manual_check")
    triggered_by = trigger_data.get("triggered_by", "system")
    priority = trigger_data.get("priority", "medium")
    details = trigger_data.get("details", {})
    
    return trigger_type, triggered_by, priority, details

def format_inventory_trigger_markdown(trigger_type: str, triggered_by: str, priority: str, details: Dict[str, Any]) -> str:
    """Format inventory trigger data for display.
    
    Args:
        trigger_type: Type of trigger
        triggered_by: What triggered the event
        priority: Priority level
        details: Additional trigger details
        
    Returns:
        Formatted markdown string
    """
    markdown = f"## Inventory Monitoring Trigger\n\n"
    markdown += f"**Type:** {trigger_type.title()}\n"
    markdown += f"**Triggered By:** {triggered_by}\n"
    markdown += f"**Priority:** {priority.upper()}\n\n"
    
    if details:
        markdown += "**Details:**\n"
        for key, value in details.items():
            markdown += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    return markdown

def format_for_display(content: Any) -> str:
    """Format content for human-readable display.
    
    Args:
        content: Content to format (can be dict, list, or string)
        
    Returns:
        Formatted string for display
    """
    if isinstance(content, dict):
        formatted = "```json\n"
        formatted += json.dumps(content, indent=2, ensure_ascii=False)
        formatted += "\n```"
        return formatted
    elif isinstance(content, list):
        if not content:
            return "No items to display"
        formatted = "\n".join(f"• {item}" for item in content)
        return formatted
    else:
        return str(content)

def create_low_stock_trigger(item_name: str, current_stock: int, reorder_level: int) -> Dict[str, Any]:
    """Create a low stock trigger for inventory monitoring.
    
    Args:
        item_name: Name of the item
        current_stock: Current stock level
        reorder_level: Reorder threshold
        
    Returns:
        Trigger data dictionary
    """
    severity = "critical" if current_stock == 0 else "high" if current_stock <= reorder_level * 0.5 else "medium"
    
    return {
        "trigger_type": "low_stock",
        "triggered_by": "system_alert",
        "priority": severity,
        "details": {
            "item_name": item_name,
            "current_stock": current_stock,
            "reorder_level": reorder_level,
            "stock_percentage": (current_stock / reorder_level * 100) if reorder_level > 0 else 0,
            "severity": severity
        }
    }

def create_sales_update_trigger(period: str, total_sales: float, total_orders: int) -> Dict[str, Any]:
    """Create a sales update trigger for inventory monitoring.
    
    Args:
        period: Time period for the update
        total_sales: Total sales amount
        total_orders: Total number of orders
        
    Returns:
        Trigger data dictionary
    """
    return {
        "trigger_type": "sales_update",
        "triggered_by": "scheduled_report",
        "priority": "low",
        "details": {
            "period": period,
            "total_sales": total_sales,
            "total_orders": total_orders,
            "avg_order_value": total_sales / total_orders if total_orders > 0 else 0
        }
    }

def create_manual_check_trigger(requested_by: str, check_type: str = "general") -> Dict[str, Any]:
    """Create a manual check trigger for inventory monitoring.
    
    Args:
        requested_by: Who requested the check
        check_type: Type of manual check
        
    Returns:
        Trigger data dictionary
    """
    return {
        "trigger_type": "manual_check",
        "triggered_by": requested_by,
        "priority": "medium",
        "details": {
            "check_type": check_type,
            "requested_by": requested_by
        }
    }

def calculate_reorder_quantity(current_stock: int, reorder_level: int, avg_daily_sales: float, lead_time_days: int = 7) -> int:
    """Calculate suggested reorder quantity based on sales velocity.
    
    Args:
        current_stock: Current stock level
        reorder_level: Minimum stock level
        avg_daily_sales: Average daily sales quantity
        lead_time_days: Lead time for restocking in days
        
    Returns:
        Suggested reorder quantity
    """
    # Calculate stock needed during lead time
    lead_time_stock = avg_daily_sales * lead_time_days
    
    # Calculate safety stock (2 weeks of average sales)
    safety_stock = avg_daily_sales * 14
    
    # Target stock level
    target_stock = lead_time_stock + safety_stock
    
    # Reorder quantity to reach target stock
    reorder_qty = max(0, int(target_stock - current_stock))
    
    # Ensure minimum reorder brings us above reorder level
    min_reorder = max(0, reorder_level - current_stock + int(safety_stock))
    
    return max(reorder_qty, min_reorder)

def assess_inventory_health(items: list) -> Dict[str, Any]:
    """Assess overall inventory health and provide insights.
    
    Args:
        items: List of inventory items
        
    Returns:
        Dictionary with health assessment
    """
    if not items:
        return {"status": "no_data", "message": "No inventory data available"}
    
    total_items = len(items)
    low_stock_items = []
    out_of_stock_items = []
    healthy_items = []
    
    total_value = 0
    
    for item in items:
        qty_available = item.get("quantity_available", 0)
        reorder_level = item.get("reorder_level", 0)
        unit_price = item.get("unit_price", 0)
        
        total_value += qty_available * unit_price
        
        if qty_available == 0:
            out_of_stock_items.append(item)
        elif qty_available <= reorder_level:
            low_stock_items.append(item)
        else:
            healthy_items.append(item)
    
    # Calculate percentages
    low_stock_pct = (len(low_stock_items) / total_items) * 100 if total_items > 0 else 0
    out_of_stock_pct = (len(out_of_stock_items) / total_items) * 100 if total_items > 0 else 0
    healthy_pct = (len(healthy_items) / total_items) * 100 if total_items > 0 else 0
    
    # Determine overall status
    if out_of_stock_pct > 10:
        status = "critical"
    elif low_stock_pct > 25:
        status = "warning"
    elif low_stock_pct > 10:
        status = "attention"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "total_items": total_items,
        "healthy_items": len(healthy_items),
        "low_stock_items": len(low_stock_items),
        "out_of_stock_items": len(out_of_stock_items),
        "healthy_percentage": healthy_pct,
        "low_stock_percentage": low_stock_pct,
        "out_of_stock_percentage": out_of_stock_pct,
        "total_inventory_value": total_value,
        "critical_items": [item["item_name"] for item in out_of_stock_items],
        "attention_items": [item["item_name"] for item in low_stock_items]
    } 