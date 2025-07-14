#!/usr/bin/env python3
"""
Example usage of the Restock Trigger Agent

This script demonstrates how to use the restock trigger agent 
with various procurement scenarios and supplier management.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.email_assistant.restock_agent_hitl_memory import restock_trigger_agent
from src.email_assistant.restock_utils import (
    create_stockout_alert_trigger,
    create_reorder_request_trigger,
    create_seasonal_prep_trigger,
    create_emergency_order_trigger,
    create_supplier_promotion_trigger,
    create_budget_cycle_trigger
)

def demo_stockout_alert():
    """Demonstrate stockout alert handling and emergency ordering"""
    print("\n🚨 Stockout Alert Demo")
    print("=" * 50)
    
    # Create a critical stockout alert for USB Cable
    trigger = create_stockout_alert_trigger(
        item_name="USB Cable",
        current_stock=2,
        reorder_level=25,
        daily_consumption=15.2
    )
    
    try:
        # Run the restock trigger agent
        result = restock_trigger_agent.invoke({
            "restock_trigger": trigger
        })
        
        print("✅ Stockout alert processed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        print(f"Priority: {result.get('priority', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error processing stockout alert: {e}")

def demo_supplier_sourcing():
    """Demonstrate supplier research and purchase order creation"""
    print("\n🏢 Supplier Sourcing Demo")
    print("=" * 50)
    
    # Create a reorder request for multiple items
    trigger = create_reorder_request_trigger(
        item_names=["Wireless Headphones", "Bluetooth Speaker"],
        quantities={"Wireless Headphones": 100, "Bluetooth Speaker": 75},
        budget_limit=15000.00
    )
    
    try:
        # Run the restock trigger agent
        result = restock_trigger_agent.invoke({
            "restock_trigger": trigger
        })
        
        print("✅ Supplier sourcing completed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error in supplier sourcing: {e}")

def demo_seasonal_preparation():
    """Demonstrate seasonal inventory preparation"""
    print("\n🌍 Seasonal Preparation Demo")
    print("=" * 50)
    
    # Create a seasonal preparation trigger for holiday season
    trigger = create_seasonal_prep_trigger(
        season="holiday",
        item_categories=["Electronics", "Accessories"],
        lead_time_buffer=45
    )
    
    try:
        # Run the restock trigger agent
        result = restock_trigger_agent.invoke({
            "restock_trigger": trigger
        })
        
        print("✅ Seasonal preparation completed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error in seasonal preparation: {e}")

def demo_emergency_ordering():
    """Demonstrate emergency order processing"""
    print("\n🚨 Emergency Ordering Demo")
    print("=" * 50)
    
    # Create an emergency order trigger
    trigger = create_emergency_order_trigger(
        item_name="Wireless Headphones",
        urgent_quantity=50,
        max_budget=5000.00,
        delivery_deadline="2025-01-20"
    )
    
    try:
        # Run the restock trigger agent
        result = restock_trigger_agent.invoke({
            "restock_trigger": trigger
        })
        
        print("✅ Emergency order processed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error in emergency ordering: {e}")

def demo_supplier_promotion():
    """Demonstrate cost-saving opportunity from supplier promotions"""
    print("\n💰 Supplier Promotion Demo")
    print("=" * 50)
    
    # Create a supplier promotion trigger
    trigger = create_supplier_promotion_trigger(
        supplier_id="SUPP001",
        promotional_items=["Wireless Headphones", "Bluetooth Speaker"],
        discount_percentage=15.0,
        promotion_end_date="2025-01-31"
    )
    
    try:
        # Run the restock trigger agent
        result = restock_trigger_agent.invoke({
            "restock_trigger": trigger
        })
        
        print("✅ Supplier promotion evaluated!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error evaluating promotion: {e}")

def demo_budget_cycle_planning():
    """Demonstrate budget cycle procurement planning"""
    print("\n📊 Budget Cycle Planning Demo")
    print("=" * 50)
    
    # Create a budget cycle trigger
    trigger = create_budget_cycle_trigger(
        budget_period="monthly",
        available_budget=20000.00,
        priority_items=["USB Cable", "Wireless Headphones"]
    )
    
    try:
        # Run the restock trigger agent
        result = restock_trigger_agent.invoke({
            "restock_trigger": trigger
        })
        
        print("✅ Budget cycle planning completed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error in budget planning: {e}")

def main():
    """Run all restock trigger agent demos"""
    print("🛒 Restock Trigger Agent Demo")
    print("=" * 60)
    print("This demo showcases the restock trigger agent capabilities")
    print("for automated supplier management and procurement workflows.")
    print()
    
    # Run demos
    demo_stockout_alert()
    demo_supplier_sourcing()
    demo_seasonal_preparation()
    demo_emergency_ordering()
    demo_supplier_promotion()
    demo_budget_cycle_planning()
    
    print("\n🎉 All restock trigger demos completed!")
    print("\nKey Features Demonstrated:")
    print("• Stockout alerts with emergency ordering workflows")
    print("• Multi-supplier research and comparison")
    print("• Purchase order creation and approval processes")
    print("• Seasonal inventory preparation planning")
    print("• Cost optimization through supplier promotions")
    print("• Budget-based procurement planning")
    print("• Human-in-the-loop approval for large orders")
    print("• Memory-based learning from procurement patterns")

if __name__ == "__main__":
    main() 