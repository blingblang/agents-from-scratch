"""
Demand forecasting tools for predicting future inventory needs.
This module provides tools to analyze sales trends and predict future demand.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from pydantic import Field, BaseModel
from langchain_core.tools import tool
import numpy as np
from statistics import mean

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing Zoho client
from .zoho_tools import zoho_client, MOCK_INVENTORY_DATA, MOCK_SALES_DATA

# Mock historical sales data for demand forecasting
MOCK_HISTORICAL_SALES = {
    "Wireless Headphones": {
        "daily_sales": [8, 6, 10, 12, 7, 9, 11, 5, 8, 14, 6, 9, 10, 7, 12],  # Last 15 days
        "weekly_sales": [45, 52, 38, 48, 41, 56, 43, 49],  # Last 8 weeks
        "seasonal_factor": 1.2,  # Higher demand in current season
        "trend_factor": 1.05  # Slight upward trend
    },
    "Bluetooth Speaker": {
        "daily_sales": [5, 4, 7, 6, 3, 5, 8, 4, 6, 9, 5, 7, 6, 4, 8],
        "weekly_sales": [35, 42, 28, 36, 31, 39, 33, 38],
        "seasonal_factor": 1.1,
        "trend_factor": 1.02
    },
    "USB Cable": {
        "daily_sales": [12, 15, 10, 18, 20, 14, 16, 8, 12, 22, 11, 15, 17, 13, 19],
        "weekly_sales": [85, 98, 72, 89, 76, 102, 81, 95],
        "seasonal_factor": 0.9,  # Lower demand in current season
        "trend_factor": 1.08
    }
}

def calculate_moving_average(data: List[float], window: int = 7) -> float:
    """Calculate moving average for demand forecasting."""
    if len(data) < window:
        return mean(data) if data else 0
    return mean(data[-window:])

def calculate_exponential_smoothing(data: List[float], alpha: float = 0.3) -> float:
    """Calculate exponentially smoothed forecast."""
    if not data:
        return 0
    if len(data) == 1:
        return data[0]
    
    forecast = data[0]
    for value in data[1:]:
        forecast = alpha * value + (1 - alpha) * forecast
    
    return forecast

def calculate_trend(data: List[float]) -> float:
    """Calculate trend coefficient from historical data."""
    if len(data) < 2:
        return 1.0
    
    # Simple linear trend calculation
    n = len(data)
    x = list(range(n))
    
    # Calculate slope
    x_mean = mean(x)
    y_mean = mean(data)
    
    numerator = sum((x[i] - x_mean) * (data[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 1.0
    
    slope = numerator / denominator
    
    # Convert to trend factor (1.0 = no trend, >1.0 = upward, <1.0 = downward)
    return 1.0 + (slope * 0.1)  # Scale slope appropriately

@tool
def analyze_demand_patterns_tool(item_name: Optional[str] = None, period_days: int = 30) -> str:
    """Analyze historical demand patterns for inventory items.
    
    Args:
        item_name: Specific item to analyze (optional, analyzes all if not provided)
        period_days: Number of days to look back for analysis
    
    Returns:
        String with demand pattern analysis
    """
    try:
        # Get current inventory
        response = zoho_client._make_request("items")
        items = response.get("items", [])
        
        if item_name:
            items = [item for item in items if item_name.lower() in item.get("item_name", "").lower()]
            
        if not items:
            return f"No items found for analysis{f' matching {item_name}' if item_name else ''}."
        
        result = f"📊 Demand Pattern Analysis ({period_days} days)\n\n"
        
        for item in items:
            name = item.get('item_name', 'Unknown')
            historical = MOCK_HISTORICAL_SALES.get(name, {
                "daily_sales": [0] * 15,
                "weekly_sales": [0] * 8,
                "seasonal_factor": 1.0,
                "trend_factor": 1.0
            })
            
            daily_sales = historical["daily_sales"]
            avg_daily = mean(daily_sales) if daily_sales else 0
            
            # Calculate trend
            trend_factor = calculate_trend(daily_sales)
            trend_direction = "📈 Increasing" if trend_factor > 1.05 else "📉 Decreasing" if trend_factor < 0.95 else "➡️ Stable"
            
            # Calculate volatility
            if len(daily_sales) > 1:
                volatility = np.std(daily_sales) / avg_daily * 100 if avg_daily > 0 else 0
            else:
                volatility = 0
            
            result += f"🔍 **{name}**\n"
            result += f"  Average Daily Sales: {avg_daily:.1f} units\n"
            result += f"  Trend: {trend_direction} (factor: {trend_factor:.2f})\n"
            result += f"  Volatility: {volatility:.1f}%\n"
            result += f"  Seasonal Factor: {historical['seasonal_factor']:.2f}\n"
            result += f"  Current Stock: {item.get('quantity_available', 0)} units\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing demand patterns: {e}")
        return f"Error analyzing demand patterns: {str(e)}"

@tool
def forecast_demand_tool(item_name: str, forecast_days: int = 7, method: str = "hybrid") -> str:
    """Forecast future demand for a specific item.
    
    Args:
        item_name: Name of the item to forecast
        forecast_days: Number of days to forecast ahead
        method: Forecasting method ('moving_average', 'exponential', 'hybrid')
    
    Returns:
        String with demand forecast and recommendations
    """
    try:
        # Get current inventory for the item
        response = zoho_client._make_request("items")
        items = response.get("items", [])
        
        target_item = None
        for item in items:
            if item_name.lower() in item.get("item_name", "").lower():
                target_item = item
                break
        
        if not target_item:
            return f"Item '{item_name}' not found in inventory."
        
        name = target_item.get('item_name', 'Unknown')
        current_stock = target_item.get('quantity_available', 0)
        reorder_level = target_item.get('reorder_level', 0)
        
        # Get historical data
        historical = MOCK_HISTORICAL_SALES.get(name, {
            "daily_sales": [1] * 15,
            "weekly_sales": [7] * 8,
            "seasonal_factor": 1.0,
            "trend_factor": 1.0
        })
        
        daily_sales = historical["daily_sales"]
        seasonal_factor = historical["seasonal_factor"]
        trend_factor = historical["trend_factor"]
        
        # Calculate base forecast using selected method
        if method == "moving_average":
            base_forecast = calculate_moving_average(daily_sales, window=7)
        elif method == "exponential":
            base_forecast = calculate_exponential_smoothing(daily_sales, alpha=0.3)
        else:  # hybrid
            ma_forecast = calculate_moving_average(daily_sales, window=7)
            exp_forecast = calculate_exponential_smoothing(daily_sales, alpha=0.3)
            base_forecast = (ma_forecast + exp_forecast) / 2
        
        # Apply seasonal and trend adjustments
        adjusted_forecast = base_forecast * seasonal_factor * trend_factor
        
        # Generate forecast for each day
        forecasts = []
        total_forecast = 0
        
        for day in range(1, forecast_days + 1):
            # Add some random variation (±20% of base forecast)
            daily_variation = 1.0 + (np.random.random() - 0.5) * 0.4
            daily_forecast = adjusted_forecast * daily_variation
            forecasts.append(daily_forecast)
            total_forecast += daily_forecast
        
        # Calculate when stock will run out
        days_until_stockout = int(current_stock / adjusted_forecast) if adjusted_forecast > 0 else 999
        
        # Generate recommendations
        recommendations = []
        if days_until_stockout <= 3:
            recommendations.append("🚨 URGENT: Stock will run out in 3 days or less!")
        elif days_until_stockout <= 7:
            recommendations.append("⚠️ WARNING: Stock will run out within a week")
        
        if total_forecast > current_stock:
            shortage = total_forecast - current_stock
            recommendations.append(f"📦 Recommend ordering {int(shortage + adjusted_forecast * 7):.0f} units (includes 1 week safety stock)")
        
        # Format results
        result = f"🔮 **Demand Forecast for {name}**\n\n"
        result += f"📈 **Forecast Details ({forecast_days} days)**\n"
        result += f"Method: {method.title()}\n"
        result += f"Base Daily Forecast: {adjusted_forecast:.1f} units/day\n"
        result += f"Total Forecasted Demand: {total_forecast:.1f} units\n\n"
        
        result += f"📊 **Current Status**\n"
        result += f"Current Stock: {current_stock} units\n"
        result += f"Reorder Level: {reorder_level} units\n"
        result += f"Days Until Stockout: {days_until_stockout} days\n\n"
        
        if recommendations:
            result += f"💡 **Recommendations**\n"
            for rec in recommendations:
                result += f"• {rec}\n"
            result += "\n"
        
        result += f"📅 **Daily Forecasts**\n"
        for i, forecast in enumerate(forecasts, 1):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            result += f"Day {i} ({date}): {forecast:.1f} units\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error forecasting demand: {e}")
        return f"Error forecasting demand: {str(e)}"

@tool
def analyze_stockout_risk_tool(minimum_days: int = 7) -> str:
    """Analyze stockout risk across all inventory items.
    
    Args:
        minimum_days: Minimum days of stock to maintain
    
    Returns:
        String with stockout risk analysis and prioritized recommendations
    """
    try:
        # Get current inventory
        response = zoho_client._make_request("items")
        items = response.get("items", [])
        
        risk_items = []
        
        for item in items:
            name = item.get('item_name', 'Unknown')
            current_stock = item.get('quantity_available', 0)
            reorder_level = item.get('reorder_level', 0)
            
            # Get historical sales data
            historical = MOCK_HISTORICAL_SALES.get(name, {
                "daily_sales": [1] * 15,
                "seasonal_factor": 1.0,
                "trend_factor": 1.0
            })
            
            daily_sales = historical["daily_sales"]
            avg_daily_sales = mean(daily_sales) if daily_sales else 1
            
            # Apply seasonal and trend adjustments
            adjusted_daily_sales = avg_daily_sales * historical["seasonal_factor"] * historical["trend_factor"]
            
            # Calculate days until stockout
            days_until_stockout = int(current_stock / adjusted_daily_sales) if adjusted_daily_sales > 0 else 999
            
            # Determine risk level
            if days_until_stockout <= 1:
                risk_level = "CRITICAL"
                priority = 1
            elif days_until_stockout <= 3:
                risk_level = "HIGH"
                priority = 2
            elif days_until_stockout <= minimum_days:
                risk_level = "MEDIUM"
                priority = 3
            else:
                risk_level = "LOW"
                priority = 4
            
            risk_items.append({
                "name": name,
                "current_stock": current_stock,
                "days_until_stockout": days_until_stockout,
                "daily_sales_rate": adjusted_daily_sales,
                "risk_level": risk_level,
                "priority": priority,
                "reorder_level": reorder_level
            })
        
        # Sort by priority and days until stockout
        risk_items.sort(key=lambda x: (x["priority"], x["days_until_stockout"]))
        
        result = f"⚠️ **Stockout Risk Analysis**\n\n"
        
        # Critical and high risk items
        critical_items = [item for item in risk_items if item["priority"] <= 2]
        if critical_items:
            result += f"🚨 **IMMEDIATE ACTION REQUIRED**\n"
            for item in critical_items:
                result += f"• **{item['name']}** - {item['risk_level']} RISK\n"
                result += f"  Current: {item['current_stock']} units\n"
                result += f"  Days until stockout: {item['days_until_stockout']}\n"
                result += f"  Daily sales rate: {item['daily_sales_rate']:.1f} units/day\n\n"
        
        # Medium risk items
        medium_items = [item for item in risk_items if item["priority"] == 3]
        if medium_items:
            result += f"⚠️ **MEDIUM RISK - PLAN REORDER**\n"
            for item in medium_items:
                result += f"• {item['name']} - {item['days_until_stockout']} days remaining\n"
            result += "\n"
        
        # Summary statistics
        high_risk_count = len([item for item in risk_items if item["priority"] <= 2])
        medium_risk_count = len([item for item in risk_items if item["priority"] == 3])
        
        result += f"📊 **Risk Summary**\n"
        result += f"Critical/High Risk Items: {high_risk_count}\n"
        result += f"Medium Risk Items: {medium_risk_count}\n"
        result += f"Total Items Analyzed: {len(risk_items)}\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing stockout risk: {e}")
        return f"Error analyzing stockout risk: {str(e)}"

@tool
def generate_reorder_recommendations_tool(lead_time_days: int = 7, safety_stock_days: int = 14) -> str:
    """Generate intelligent reorder recommendations based on demand forecasts.
    
    Args:
        lead_time_days: Expected lead time for restocking
        safety_stock_days: Days of safety stock to maintain
    
    Returns:
        String with detailed reorder recommendations
    """
    try:
        # Get current inventory
        response = zoho_client._make_request("items")
        items = response.get("items", [])
        
        recommendations = []
        
        for item in items:
            name = item.get('item_name', 'Unknown')
            current_stock = item.get('quantity_available', 0)
            reorder_level = item.get('reorder_level', 0)
            unit_price = item.get('unit_price', 0)
            
            # Get historical sales data
            historical = MOCK_HISTORICAL_SALES.get(name, {
                "daily_sales": [1] * 15,
                "seasonal_factor": 1.0,
                "trend_factor": 1.0
            })
            
            daily_sales = historical["daily_sales"]
            avg_daily_sales = mean(daily_sales) if daily_sales else 1
            
            # Apply seasonal and trend adjustments
            adjusted_daily_sales = avg_daily_sales * historical["seasonal_factor"] * historical["trend_factor"]
            
            # Calculate required stock levels
            lead_time_stock = adjusted_daily_sales * lead_time_days
            safety_stock = adjusted_daily_sales * safety_stock_days
            optimal_stock_level = lead_time_stock + safety_stock
            
            # Calculate reorder recommendation
            if current_stock <= reorder_level or current_stock < optimal_stock_level * 0.8:
                reorder_quantity = max(
                    optimal_stock_level - current_stock,
                    adjusted_daily_sales * (lead_time_days + safety_stock_days)
                )
                
                # Round up to reasonable order quantities
                if reorder_quantity < 10:
                    reorder_quantity = int(reorder_quantity) + 1
                else:
                    reorder_quantity = int(reorder_quantity / 5) * 5 + 5  # Round to nearest 5
                
                total_cost = reorder_quantity * unit_price
                
                # Determine urgency
                days_until_stockout = int(current_stock / adjusted_daily_sales) if adjusted_daily_sales > 0 else 999
                if days_until_stockout <= 3:
                    urgency = "URGENT"
                elif days_until_stockout <= 7:
                    urgency = "HIGH"
                else:
                    urgency = "MEDIUM"
                
                recommendations.append({
                    "name": name,
                    "current_stock": current_stock,
                    "reorder_quantity": int(reorder_quantity),
                    "total_cost": total_cost,
                    "urgency": urgency,
                    "days_until_stockout": days_until_stockout,
                    "daily_sales_rate": adjusted_daily_sales
                })
        
        # Sort by urgency and days until stockout
        urgency_order = {"URGENT": 1, "HIGH": 2, "MEDIUM": 3}
        recommendations.sort(key=lambda x: (urgency_order.get(x["urgency"], 4), x["days_until_stockout"]))
        
        if not recommendations:
            return "✅ No reorder recommendations needed. All items have adequate stock levels."
        
        result = f"📋 **Intelligent Reorder Recommendations**\n\n"
        
        total_investment = sum(rec["total_cost"] for rec in recommendations)
        result += f"💰 **Total Investment Required: ${total_investment:.2f}**\n\n"
        
        # Group by urgency
        urgent_items = [rec for rec in recommendations if rec["urgency"] == "URGENT"]
        high_items = [rec for rec in recommendations if rec["urgency"] == "HIGH"]
        medium_items = [rec for rec in recommendations if rec["urgency"] == "MEDIUM"]
        
        if urgent_items:
            result += f"🚨 **URGENT ORDERS (Place Today)**\n"
            urgent_cost = 0
            for rec in urgent_items:
                result += f"• **{rec['name']}**\n"
                result += f"  Order Quantity: {rec['reorder_quantity']} units\n"
                result += f"  Cost: ${rec['total_cost']:.2f}\n"
                result += f"  Current Stock: {rec['current_stock']} units\n"
                result += f"  Days Until Stockout: {rec['days_until_stockout']}\n\n"
                urgent_cost += rec['total_cost']
            result += f"Urgent Orders Subtotal: ${urgent_cost:.2f}\n\n"
        
        if high_items:
            result += f"⚠️ **HIGH PRIORITY (Place This Week)**\n"
            high_cost = 0
            for rec in high_items:
                result += f"• {rec['name']} - {rec['reorder_quantity']} units (${rec['total_cost']:.2f})\n"
                high_cost += rec['total_cost']
            result += f"High Priority Subtotal: ${high_cost:.2f}\n\n"
        
        if medium_items:
            result += f"📝 **MEDIUM PRIORITY (Plan for Next Week)**\n"
            medium_cost = 0
            for rec in medium_items:
                result += f"• {rec['name']} - {rec['reorder_quantity']} units (${rec['total_cost']:.2f})\n"
                medium_cost += rec['total_cost']
            result += f"Medium Priority Subtotal: ${medium_cost:.2f}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating reorder recommendations: {e}")
        return f"Error generating reorder recommendations: {str(e)}"

@tool
def seasonal_demand_analysis_tool(item_name: Optional[str] = None) -> str:
    """Analyze seasonal demand patterns and provide seasonal forecasting insights.
    
    Args:
        item_name: Specific item to analyze (optional)
    
    Returns:
        String with seasonal demand analysis
    """
    try:
        # Get current inventory
        response = zoho_client._make_request("items")
        items = response.get("items", [])
        
        if item_name:
            items = [item for item in items if item_name.lower() in item.get("item_name", "").lower()]
            
        if not items:
            return f"No items found for seasonal analysis{f' matching {item_name}' if item_name else ''}."
        
        result = f"🌍 **Seasonal Demand Analysis**\n\n"
        
        # Mock seasonal data for demonstration
        seasonal_insights = {
            "Wireless Headphones": {
                "peak_season": "Holiday Season (Nov-Dec)",
                "low_season": "Summer (Jun-Aug)",
                "seasonal_variance": 45,
                "recommendations": ["Stock up 40% before holidays", "Reduce inventory in summer"]
            },
            "Bluetooth Speaker": {
                "peak_season": "Summer (Jun-Aug)",
                "low_season": "Winter (Jan-Feb)",
                "seasonal_variance": 35,
                "recommendations": ["Summer demand increases by 60%", "Consider promotional pricing in winter"]
            },
            "USB Cable": {
                "peak_season": "Back-to-school (Aug-Sep)",
                "low_season": "Spring (Mar-May)",
                "seasonal_variance": 25,
                "recommendations": ["Steady demand with school season spikes", "Maintain consistent stock levels"]
            }
        }
        
        for item in items:
            name = item.get('item_name', 'Unknown')
            historical = MOCK_HISTORICAL_SALES.get(name, {})
            insights = seasonal_insights.get(name, {
                "peak_season": "Unknown",
                "low_season": "Unknown", 
                "seasonal_variance": 0,
                "recommendations": ["Insufficient data for seasonal analysis"]
            })
            
            current_factor = historical.get("seasonal_factor", 1.0)
            season_status = "High Demand" if current_factor > 1.1 else "Low Demand" if current_factor < 0.9 else "Normal Demand"
            
            result += f"📊 **{name}**\n"
            result += f"  Current Seasonal Status: {season_status} (factor: {current_factor:.2f})\n"
            result += f"  Peak Season: {insights['peak_season']}\n"
            result += f"  Low Season: {insights['low_season']}\n"
            result += f"  Seasonal Variance: ±{insights['seasonal_variance']}%\n"
            result += f"  Current Stock: {item.get('quantity_available', 0)} units\n\n"
            
            result += f"  📝 **Seasonal Recommendations:**\n"
            for rec in insights['recommendations']:
                result += f"  • {rec}\n"
            result += "\n"
        
        # Add general seasonal insights
        result += f"🌟 **General Seasonal Insights**\n"
        result += f"• Monitor weather patterns and holidays for demand spikes\n"
        result += f"• Adjust safety stock levels based on seasonal variance\n"
        result += f"• Plan promotions during low-demand periods\n"
        result += f"• Consider lead times when preparing for peak seasons\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing seasonal demand: {e}")
        return f"Error analyzing seasonal demand: {str(e)}"

# Export all tools for easy importing
__all__ = [
    "analyze_demand_patterns_tool",
    "forecast_demand_tool",
    "analyze_stockout_risk_tool", 
    "generate_reorder_recommendations_tool",
    "seasonal_demand_analysis_tool"
] 