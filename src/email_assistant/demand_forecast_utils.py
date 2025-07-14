"""Utility functions for the demand forecasting agent."""

from typing import Dict, Any, Tuple
import json
from datetime import datetime, timedelta

def parse_forecast_trigger(trigger_data: Dict[str, Any]) -> Tuple[str, str, str, Dict[str, Any]]:
    """Parse demand forecast trigger data into components.
    
    Args:
        trigger_data: Dictionary containing forecast trigger information
        
    Returns:
        Tuple of (trigger_type, triggered_by, priority, details)
    """
    trigger_type = trigger_data.get("trigger_type", "forecast_request")
    triggered_by = trigger_data.get("triggered_by", "system")
    priority = trigger_data.get("priority", "medium")
    details = trigger_data.get("details", {})
    
    return trigger_type, triggered_by, priority, details

def format_forecast_trigger_markdown(trigger_type: str, triggered_by: str, priority: str, details: Dict[str, Any]) -> str:
    """Format forecast trigger data for display.
    
    Args:
        trigger_type: Type of forecast trigger
        triggered_by: What triggered the forecast request
        priority: Priority level
        details: Additional trigger details
        
    Returns:
        Formatted markdown string
    """
    markdown = f"## 🔮 Demand Forecast Request\n\n"
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

def format_forecast_for_display(forecast_data: Any) -> str:
    """Format forecast content for human-readable display.
    
    Args:
        forecast_data: Forecast content to format (can be dict, list, or string)
        
    Returns:
        Formatted string for display
    """
    if isinstance(forecast_data, dict):
        formatted = "```json\n"
        formatted += json.dumps(forecast_data, indent=2, ensure_ascii=False, default=str)
        formatted += "\n```"
        return formatted
    elif isinstance(forecast_data, list):
        if not forecast_data:
            return "No forecast data to display"
        formatted = "\n".join(f"• {item}" for item in forecast_data)
        return formatted
    else:
        return str(forecast_data)

def create_stockout_risk_trigger(item_name: str, current_stock: int, daily_sales_rate: float) -> Dict[str, Any]:
    """Create a stockout risk trigger for demand forecasting.
    
    Args:
        item_name: Name of the item at risk
        current_stock: Current stock level
        daily_sales_rate: Average daily sales rate
        
    Returns:
        Forecast trigger data dictionary
    """
    days_until_stockout = int(current_stock / daily_sales_rate) if daily_sales_rate > 0 else 999
    
    if days_until_stockout <= 1:
        priority = "critical"
        severity = "critical"
    elif days_until_stockout <= 3:
        priority = "high"
        severity = "high"
    elif days_until_stockout <= 7:
        priority = "medium" 
        severity = "medium"
    else:
        priority = "low"
        severity = "low"
    
    return {
        "trigger_type": "stockout_risk",
        "triggered_by": "inventory_monitoring",
        "priority": priority,
        "details": {
            "item_name": item_name,
            "current_stock": current_stock,
            "daily_sales_rate": daily_sales_rate,
            "days_until_stockout": days_until_stockout,
            "severity": severity,
            "forecast_horizon": max(14, days_until_stockout + 7)  # At least 2 weeks ahead
        }
    }

def create_forecast_request_trigger(item_names: list = None, forecast_days: int = 7, method: str = "hybrid") -> Dict[str, Any]:
    """Create a general forecast request trigger.
    
    Args:
        item_names: List of specific items to forecast (optional)
        forecast_days: Number of days to forecast ahead
        method: Preferred forecasting method
        
    Returns:
        Forecast trigger data dictionary
    """
    return {
        "trigger_type": "forecast_request",
        "triggered_by": "user_request",
        "priority": "medium",
        "details": {
            "item_scope": item_names or "all_items",
            "forecast_horizon": forecast_days,
            "method": method,
            "request_timestamp": datetime.now().isoformat()
        }
    }

def create_seasonal_analysis_trigger(item_names: list = None) -> Dict[str, Any]:
    """Create a seasonal analysis trigger for demand forecasting.
    
    Args:
        item_names: List of specific items to analyze (optional)
        
    Returns:
        Forecast trigger data dictionary
    """
    return {
        "trigger_type": "seasonal_analysis",
        "triggered_by": "business_planning",
        "priority": "medium",
        "details": {
            "item_scope": item_names or "all_items",
            "analysis_type": "seasonal_patterns",
            "current_season": get_current_season(),
            "request_timestamp": datetime.now().isoformat()
        }
    }

def create_reorder_planning_trigger(lead_time_days: int = 7, safety_stock_days: int = 14) -> Dict[str, Any]:
    """Create a reorder planning trigger for demand forecasting.
    
    Args:
        lead_time_days: Expected lead time for restocking
        safety_stock_days: Days of safety stock to maintain
        
    Returns:
        Forecast trigger data dictionary
    """
    return {
        "trigger_type": "reorder_planning",
        "triggered_by": "procurement_planning",
        "priority": "high",
        "details": {
            "lead_time_days": lead_time_days,
            "safety_stock_days": safety_stock_days,
            "planning_horizon": lead_time_days + safety_stock_days + 7,  # Extra buffer
            "analysis_scope": "all_items",
            "request_timestamp": datetime.now().isoformat()
        }
    }

def create_pattern_analysis_trigger(item_names: list = None, period_days: int = 30) -> Dict[str, Any]:
    """Create a pattern analysis trigger for demand forecasting.
    
    Args:
        item_names: List of specific items to analyze (optional) 
        period_days: Number of days to analyze patterns for
        
    Returns:
        Forecast trigger data dictionary
    """
    return {
        "trigger_type": "pattern_analysis",
        "triggered_by": "analytics_request",
        "priority": "medium",
        "details": {
            "item_scope": item_names or "all_items",
            "analysis_period": period_days,
            "analysis_types": ["trend", "seasonality", "volatility"],
            "request_timestamp": datetime.now().isoformat()
        }
    }

def create_accuracy_review_trigger(forecasting_methods: list = None) -> Dict[str, Any]:
    """Create an accuracy review trigger for demand forecasting.
    
    Args:
        forecasting_methods: List of methods to review (optional)
        
    Returns:
        Forecast trigger data dictionary
    """
    return {
        "trigger_type": "accuracy_review",
        "triggered_by": "performance_monitoring",
        "priority": "low",
        "details": {
            "methods_to_review": forecasting_methods or ["moving_average", "exponential", "hybrid"],
            "review_period": 30,  # Last 30 days
            "metrics": ["accuracy", "bias", "mean_absolute_error"],
            "request_timestamp": datetime.now().isoformat()
        }
    }

def get_current_season() -> str:
    """Get the current season based on the date.
    
    Returns:
        String representing the current season
    """
    month = datetime.now().month
    
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "unknown"

def calculate_forecast_confidence(historical_accuracy: float, data_quality: float, trend_stability: float) -> float:
    """Calculate overall forecast confidence based on multiple factors.
    
    Args:
        historical_accuracy: Past forecasting accuracy (0-1)
        data_quality: Quality of available data (0-1) 
        trend_stability: Stability of demand trends (0-1)
        
    Returns:
        Overall confidence level (0-1)
    """
    # Weighted average of factors
    weights = [0.5, 0.3, 0.2]  # Accuracy most important, then data quality, then stability
    factors = [historical_accuracy, data_quality, trend_stability]
    
    confidence = sum(w * f for w, f in zip(weights, factors))
    return max(0.0, min(1.0, confidence))  # Clamp to 0-1 range

def format_confidence_level(confidence: float) -> str:
    """Format confidence level for display.
    
    Args:
        confidence: Confidence level (0-1)
        
    Returns:
        Human-readable confidence description
    """
    if confidence >= 0.9:
        return f"Very High ({confidence:.0%})"
    elif confidence >= 0.8:
        return f"High ({confidence:.0%})"
    elif confidence >= 0.7:
        return f"Moderate ({confidence:.0%})"
    elif confidence >= 0.6:
        return f"Low ({confidence:.0%})"
    else:
        return f"Very Low ({confidence:.0%})"

def calculate_safety_stock(avg_daily_demand: float, max_daily_demand: float, lead_time_days: int, service_level: float = 0.95) -> int:
    """Calculate recommended safety stock levels.
    
    Args:
        avg_daily_demand: Average daily demand
        max_daily_demand: Maximum observed daily demand
        lead_time_days: Lead time in days
        service_level: Desired service level (0-1)
        
    Returns:
        Recommended safety stock quantity
    """
    # Simple safety stock calculation
    demand_variability = max_daily_demand - avg_daily_demand
    safety_factor = 1.65 if service_level >= 0.95 else 1.28 if service_level >= 0.90 else 1.04
    
    safety_stock = demand_variability * safety_factor * (lead_time_days ** 0.5)
    return max(0, int(safety_stock))

def optimize_reorder_point(avg_daily_demand: float, lead_time_days: int, safety_stock: int) -> int:
    """Calculate optimal reorder point.
    
    Args:
        avg_daily_demand: Average daily demand
        lead_time_days: Lead time in days
        safety_stock: Safety stock quantity
        
    Returns:
        Optimal reorder point
    """
    lead_time_demand = avg_daily_demand * lead_time_days
    reorder_point = lead_time_demand + safety_stock
    return max(1, int(reorder_point)) 