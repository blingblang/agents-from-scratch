"""Utility functions for the restock trigger agent."""

from typing import Dict, Any, Tuple
import json
from datetime import datetime, timedelta

def parse_restock_trigger(trigger_data: Dict[str, Any]) -> Tuple[str, str, str, Dict[str, Any]]:
    """Parse restock trigger data into components.
    
    Args:
        trigger_data: Dictionary containing restock trigger information
        
    Returns:
        Tuple of (trigger_type, triggered_by, priority, details)
    """
    trigger_type = trigger_data.get("trigger_type", "reorder_request")
    triggered_by = trigger_data.get("triggered_by", "system")
    priority = trigger_data.get("priority", "medium")
    details = trigger_data.get("details", {})
    
    return trigger_type, triggered_by, priority, details

def format_restock_trigger_markdown(trigger_type: str, triggered_by: str, priority: str, details: Dict[str, Any]) -> str:
    """Format restock trigger data for display.
    
    Args:
        trigger_type: Type of restock trigger
        triggered_by: What triggered the restock request
        priority: Priority level
        details: Additional trigger details
        
    Returns:
        Formatted markdown string
    """
    markdown = f"## 🛒 Restock Request\n\n"
    markdown += f"**Type:** {trigger_type.replace('_', ' ').title()}\n"
    markdown += f"**Triggered By:** {triggered_by}\n"
    markdown += f"**Priority:** {priority.upper()}\n\n"
    
    if details:
        markdown += "**Request Details:**\n"
        for key, value in details.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            markdown += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    return markdown

def format_restock_for_display(restock_data: Any) -> str:
    """Format restock content for human-readable display.
    
    Args:
        restock_data: Restock content to format (can be dict, list, or string)
        
    Returns:
        Formatted string for display
    """
    if isinstance(restock_data, dict):
        formatted = "```json\n"
        formatted += json.dumps(restock_data, indent=2, ensure_ascii=False, default=str)
        formatted += "\n```"
        return formatted
    elif isinstance(restock_data, list):
        if not restock_data:
            return "No restock data to display"
        formatted = "\n".join(f"• {item}" for item in restock_data)
        return formatted
    else:
        return str(restock_data)

def create_stockout_alert_trigger(item_name: str, current_stock: int, reorder_level: int, daily_consumption: float) -> Dict[str, Any]:
    """Create a stockout alert trigger for restocking.
    
    Args:
        item_name: Name of the item at risk of stockout
        current_stock: Current stock level
        reorder_level: Reorder threshold
        daily_consumption: Average daily consumption rate
        
    Returns:
        Restock trigger data dictionary
    """
    days_until_stockout = int(current_stock / daily_consumption) if daily_consumption > 0 else 999
    
    if days_until_stockout <= 1:
        priority = "critical"
        urgency = "emergency"
    elif days_until_stockout <= 3:
        priority = "high"
        urgency = "urgent"
    elif days_until_stockout <= 7:
        priority = "medium"
        urgency = "soon"
    else:
        priority = "low"
        urgency = "routine"
    
    # Calculate suggested order quantity (2-3 weeks of supply)
    suggested_quantity = max(reorder_level - current_stock, int(daily_consumption * 21))
    
    return {
        "trigger_type": "stockout_alert",
        "triggered_by": "inventory_monitoring",
        "priority": priority,
        "details": {
            "item_name": item_name,
            "current_stock": current_stock,
            "reorder_level": reorder_level,
            "daily_consumption": daily_consumption,
            "days_until_stockout": days_until_stockout,
            "urgency": urgency,
            "suggested_quantity": suggested_quantity,
            "stock_percentage": (current_stock / reorder_level * 100) if reorder_level > 0 else 0
        },
        "items_affected": [item_name],
        "delivery_deadline": (datetime.now() + timedelta(days=max(7, days_until_stockout - 1))).strftime("%Y-%m-%d")
    }

def create_reorder_request_trigger(item_names: list = None, quantities: Dict[str, int] = None, budget_limit: float = None) -> Dict[str, Any]:
    """Create a general reorder request trigger.
    
    Args:
        item_names: List of items to reorder
        quantities: Dictionary mapping item names to quantities
        budget_limit: Optional budget constraint
        
    Returns:
        Restock trigger data dictionary
    """
    return {
        "trigger_type": "reorder_request",
        "triggered_by": "procurement_planning",
        "priority": "medium",
        "details": {
            "item_scope": item_names or "multiple_items",
            "quantities": quantities or {},
            "budget_limit": budget_limit,
            "request_timestamp": datetime.now().isoformat(),
            "request_type": "standard_reorder"
        },
        "items_affected": item_names or [],
        "budget_limit": budget_limit
    }

def create_seasonal_prep_trigger(season: str, item_categories: list = None, lead_time_buffer: int = 30) -> Dict[str, Any]:
    """Create a seasonal preparation trigger for restocking.
    
    Args:
        season: Target season (spring, summer, fall, winter, holiday)
        item_categories: Categories of items to prepare for
        lead_time_buffer: Days ahead to prepare
        
    Returns:
        Restock trigger data dictionary
    """
    preparation_date = datetime.now() + timedelta(days=lead_time_buffer)
    
    return {
        "trigger_type": "seasonal_prep",
        "triggered_by": "seasonal_planning",
        "priority": "medium",
        "details": {
            "target_season": season,
            "item_categories": item_categories or ["all_categories"],
            "preparation_date": preparation_date.strftime("%Y-%m-%d"),
            "lead_time_buffer": lead_time_buffer,
            "planning_type": "seasonal_demand"
        },
        "delivery_deadline": preparation_date.strftime("%Y-%m-%d")
    }

def create_emergency_order_trigger(item_name: str, urgent_quantity: int, max_budget: float, delivery_deadline: str) -> Dict[str, Any]:
    """Create an emergency order trigger for critical restocking.
    
    Args:
        item_name: Critical item needing immediate restocking
        urgent_quantity: Quantity needed urgently
        max_budget: Maximum budget for emergency order
        delivery_deadline: Required delivery date (YYYY-MM-DD)
        
    Returns:
        Restock trigger data dictionary
    """
    return {
        "trigger_type": "emergency_order",
        "triggered_by": "urgent_demand",
        "priority": "critical",
        "details": {
            "item_name": item_name,
            "urgent_quantity": urgent_quantity,
            "max_budget": max_budget,
            "delivery_deadline": delivery_deadline,
            "emergency_level": "critical",
            "expedited_shipping": True,
            "request_timestamp": datetime.now().isoformat()
        },
        "items_affected": [item_name],
        "budget_limit": max_budget,
        "delivery_deadline": delivery_deadline
    }

def create_supplier_promotion_trigger(supplier_id: str, promotional_items: list, discount_percentage: float, promotion_end_date: str) -> Dict[str, Any]:
    """Create a supplier promotion trigger for cost-saving restocking.
    
    Args:
        supplier_id: ID of supplier offering promotion
        promotional_items: List of items on promotion
        discount_percentage: Percentage discount offered
        promotion_end_date: When promotion ends (YYYY-MM-DD)
        
    Returns:
        Restock trigger data dictionary
    """
    return {
        "trigger_type": "supplier_promotion",
        "triggered_by": f"supplier_{supplier_id}",
        "priority": "medium",
        "details": {
            "supplier_id": supplier_id,
            "promotional_items": promotional_items,
            "discount_percentage": discount_percentage,
            "promotion_end_date": promotion_end_date,
            "savings_opportunity": True,
            "bulk_order_recommended": True
        },
        "items_affected": promotional_items,
        "delivery_deadline": promotion_end_date
    }

def create_budget_cycle_trigger(budget_period: str, available_budget: float, priority_items: list = None) -> Dict[str, Any]:
    """Create a budget cycle trigger for planned restocking.
    
    Args:
        budget_period: Budget period (monthly, quarterly, yearly)
        available_budget: Available budget for this cycle
        priority_items: High-priority items to restock
        
    Returns:
        Restock trigger data dictionary
    """
    return {
        "trigger_type": "budget_cycle",
        "triggered_by": "budget_planning",
        "priority": "low",
        "details": {
            "budget_period": budget_period,
            "available_budget": available_budget,
            "priority_items": priority_items or [],
            "cycle_start": datetime.now().strftime("%Y-%m-%d"),
            "planning_horizon": "30_days",
            "cost_optimization_focus": True
        },
        "budget_limit": available_budget
    }

def calculate_reorder_quantity(current_stock: int, reorder_level: int, target_stock: int, daily_consumption: float, lead_time_days: int = 7) -> int:
    """Calculate optimal reorder quantity.
    
    Args:
        current_stock: Current stock level
        reorder_level: Minimum stock threshold
        target_stock: Desired stock level
        daily_consumption: Average daily consumption
        lead_time_days: Supplier lead time
        
    Returns:
        Recommended reorder quantity
    """
    # Calculate stock needed during lead time
    lead_time_stock = daily_consumption * lead_time_days
    
    # Calculate safety stock (1 week buffer)
    safety_stock = daily_consumption * 7
    
    # Target stock should cover lead time + safety stock
    optimal_target = lead_time_stock + safety_stock
    
    # Use higher of user target or calculated optimal
    final_target = max(target_stock, optimal_target)
    
    # Reorder quantity to reach target
    reorder_qty = max(0, int(final_target - current_stock))
    
    # Ensure minimum reorder brings us above reorder level
    min_reorder = max(0, reorder_level - current_stock + int(safety_stock))
    
    return max(reorder_qty, min_reorder)

def estimate_delivery_date(order_date: datetime, lead_time_days: int, expedited: bool = False) -> datetime:
    """Estimate delivery date based on lead time.
    
    Args:
        order_date: Date when order is placed
        lead_time_days: Standard lead time in days
        expedited: Whether expedited shipping is used
        
    Returns:
        Estimated delivery date
    """
    # Expedited shipping reduces lead time by 40%
    if expedited:
        lead_time_days = int(lead_time_days * 0.6)
    
    # Add weekend buffer for realistic delivery
    delivery_date = order_date + timedelta(days=lead_time_days)
    
    # If delivery falls on weekend, move to Monday
    if delivery_date.weekday() >= 5:  # Saturday or Sunday
        delivery_date += timedelta(days=(7 - delivery_date.weekday()))
    
    return delivery_date

def calculate_bulk_savings(unit_price: float, quantity: int, bulk_thresholds: Dict[int, float]) -> Tuple[float, float]:
    """Calculate bulk pricing and savings.
    
    Args:
        unit_price: Base unit price
        quantity: Order quantity
        bulk_thresholds: Dictionary mapping quantities to discount percentages
        
    Returns:
        Tuple of (final_unit_price, total_savings)
    """
    applicable_discount = 0.0
    
    # Find highest applicable bulk discount
    for threshold_qty, discount in sorted(bulk_thresholds.items(), reverse=True):
        if quantity >= threshold_qty:
            applicable_discount = discount
            break
    
    final_unit_price = unit_price * (1 - applicable_discount)
    total_savings = (unit_price - final_unit_price) * quantity
    
    return final_unit_price, total_savings

def format_supplier_comparison(suppliers: list) -> str:
    """Format supplier comparison for easy reading.
    
    Args:
        suppliers: List of supplier quote dictionaries
        
    Returns:
        Formatted comparison string
    """
    if not suppliers:
        return "No suppliers available for comparison."
    
    # Sort by total cost
    sorted_suppliers = sorted(suppliers, key=lambda x: x.get('total_cost', float('inf')))
    
    result = "📊 **Supplier Comparison:**\n\n"
    
    for i, supplier in enumerate(sorted_suppliers, 1):
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        result += f"{rank_emoji} **{supplier.get('supplier_name', 'Unknown')}**\n"
        result += f"   💰 Total Cost: ${supplier.get('total_cost', 0):.2f}\n"
        result += f"   📊 Unit Price: ${supplier.get('final_price', 0):.2f}\n"
        result += f"   🚚 Lead Time: {supplier.get('lead_time_days', 'Unknown')} days\n"
        result += f"   ⭐ Rating: {supplier.get('rating', 'N/A')}/5\n"
        result += f"   💳 Terms: {supplier.get('payment_terms', 'Unknown')}\n"
        
        if supplier.get('bulk_discount_applied'):
            result += f"   🎯 Bulk Discount Applied\n"
        
        result += "\n"
    
    return result

def validate_budget_limit(total_cost: float, budget_limit: float = None) -> Tuple[bool, str]:
    """Validate if order fits within budget constraints.
    
    Args:
        total_cost: Total cost of the order
        budget_limit: Budget limit (optional)
        
    Returns:
        Tuple of (within_budget, message)
    """
    if budget_limit is None:
        return True, "No budget limit specified"
    
    if total_cost <= budget_limit:
        remaining = budget_limit - total_cost
        return True, f"Within budget. Remaining: ${remaining:.2f}"
    else:
        overage = total_cost - budget_limit
        return False, f"Over budget by ${overage:.2f}"

def prioritize_restock_items(items: list, budget_limit: float = None) -> list:
    """Prioritize restock items based on urgency and cost.
    
    Args:
        items: List of item dictionaries with priority and cost info
        budget_limit: Optional budget constraint
        
    Returns:
        Prioritized list of items
    """
    # Priority weights
    priority_weights = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }
    
    # Sort by priority (descending) then by cost (ascending)
    sorted_items = sorted(
        items,
        key=lambda x: (
            -priority_weights.get(x.get('priority', 'low'), 1),
            x.get('total_cost', 0)
        )
    )
    
    # If budget limit exists, select items that fit
    if budget_limit:
        selected_items = []
        running_total = 0
        
        for item in sorted_items:
            item_cost = item.get('total_cost', 0)
            if running_total + item_cost <= budget_limit:
                selected_items.append(item)
                running_total += item_cost
            elif item.get('priority') == 'critical':
                # Always include critical items even if over budget
                selected_items.append(item)
        
        return selected_items
    
    return sorted_items 