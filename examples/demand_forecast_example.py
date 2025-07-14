#!/usr/bin/env python3
"""
Example usage of the Demand Forecast Agent

This script demonstrates how to use the demand forecasting agent 
with various scenarios and triggers.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.email_assistant.demand_forecast_agent_hitl_memory import demand_forecast_agent
from src.email_assistant.demand_forecast_utils import (
    create_stockout_risk_trigger,
    create_forecast_request_trigger,
    create_seasonal_analysis_trigger,
    create_reorder_planning_trigger,
    create_pattern_analysis_trigger
)

def demo_stockout_risk_analysis():
    """Demonstrate stockout risk analysis and demand forecasting"""
    print("\n🚨 Stockout Risk Analysis Demo")
    print("=" * 50)
    
    # Create a stockout risk trigger for USB Cable (low stock situation)
    trigger = create_stockout_risk_trigger(
        item_name="USB Cable",
        current_stock=5,
        daily_sales_rate=15.2
    )
    
    try:
        # Run the demand forecast agent
        result = demand_forecast_agent.invoke({
            "forecast_trigger": trigger
        })
        
        print("✅ Stockout risk analysis completed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        print(f"Priority: {result.get('priority', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error in stockout analysis: {e}")

def demo_demand_forecasting():
    """Demonstrate demand forecasting for specific items"""
    print("\n📈 Demand Forecasting Demo")
    print("=" * 50)
    
    # Create a forecast request for Wireless Headphones
    trigger = create_forecast_request_trigger(
        item_names=["Wireless Headphones"],
        forecast_days=14,
        method="hybrid"
    )
    
    try:
        # Run the demand forecast agent
        result = demand_forecast_agent.invoke({
            "forecast_trigger": trigger
        })
        
        print("✅ Demand forecast generated!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error in demand forecasting: {e}")

def demo_seasonal_analysis():
    """Demonstrate seasonal demand pattern analysis"""
    print("\n🌍 Seasonal Analysis Demo")
    print("=" * 50)
    
    # Create a seasonal analysis trigger
    trigger = create_seasonal_analysis_trigger(
        item_names=["Bluetooth Speaker", "Wireless Headphones"]
    )
    
    try:
        # Run the demand forecast agent
        result = demand_forecast_agent.invoke({
            "forecast_trigger": trigger
        })
        
        print("✅ Seasonal analysis completed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error in seasonal analysis: {e}")

def demo_reorder_planning():
    """Demonstrate intelligent reorder planning"""
    print("\n📋 Reorder Planning Demo")
    print("=" * 50)
    
    # Create a reorder planning trigger
    trigger = create_reorder_planning_trigger(
        lead_time_days=7,
        safety_stock_days=14
    )
    
    try:
        # Run the demand forecast agent
        result = demand_forecast_agent.invoke({
            "forecast_trigger": trigger
        })
        
        print("✅ Reorder planning completed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error in reorder planning: {e}")

def demo_pattern_analysis():
    """Demonstrate demand pattern analysis"""
    print("\n📊 Pattern Analysis Demo")
    print("=" * 50)
    
    # Create a pattern analysis trigger
    trigger = create_pattern_analysis_trigger(
        item_names=["USB Cable"],
        period_days=30
    )
    
    try:
        # Run the demand forecast agent
        result = demand_forecast_agent.invoke({
            "forecast_trigger": trigger
        })
        
        print("✅ Pattern analysis completed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error in pattern analysis: {e}")

def main():
    """Run all demand forecasting demos"""
    print("🔮 Demand Forecast Agent Demo")
    print("=" * 60)
    print("This demo showcases the demand forecasting agent capabilities")
    print("using mock data from Zoho Inventory integration.")
    print()
    
    # Run demos
    demo_stockout_risk_analysis()
    demo_demand_forecasting()
    demo_seasonal_analysis()
    demo_reorder_planning()
    demo_pattern_analysis()
    
    print("\n🎉 All demand forecasting demos completed!")
    print("\nKey Features Demonstrated:")
    print("• Stockout risk analysis with critical alerts")
    print("• Multi-method demand forecasting (moving average, exponential, hybrid)")
    print("• Seasonal pattern analysis and adjustments")
    print("• Intelligent reorder recommendations with cost analysis")
    print("• Historical pattern analysis and trend detection")
    print("• Human-in-the-loop decision making for critical actions")
    print("• Memory-based learning from user preferences")

if __name__ == "__main__":
    main() 