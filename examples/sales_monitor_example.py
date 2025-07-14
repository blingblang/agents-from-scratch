"""
Example usage of the Sales Monitor Agent for Zoho Inventory

This script demonstrates how to use the sales monitor agent to:
1. Check inventory levels
2. Handle low stock alerts
3. Generate sales analytics
4. Create orders with approval
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from email_assistant.sales_monitor_agent_hitl_memory import sales_monitor_agent
from email_assistant.inventory_utils import (
    create_low_stock_trigger,
    create_sales_update_trigger,
    create_manual_check_trigger
)

def demo_inventory_check():
    """Demonstrate a basic inventory check"""
    print("🔍 Running Inventory Check...")
    print("=" * 50)
    
    # Create a manual check trigger
    trigger = create_manual_check_trigger("demo_user", "general")
    
    try:
        # Run the agent
        result = sales_monitor_agent.invoke({
            "inventory_trigger": trigger
        })
        
        print("✅ Inventory check completed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        print(f"Priority: {result.get('priority', 'unknown')}")
        
        # Print the last message from the agent
        messages = result.get('messages', [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                print(f"Response: {last_message.content}")
    
    except Exception as e:
        print(f"❌ Error during inventory check: {e}")

def demo_low_stock_alert():
    """Demonstrate handling a low stock alert"""
    print("\n⚠️ Simulating Low Stock Alert...")
    print("=" * 50)
    
    # Create a low stock trigger for USB Cable (5 units, reorder at 25)
    trigger = create_low_stock_trigger("USB Cable", 5, 25)
    
    try:
        # Run the agent
        result = sales_monitor_agent.invoke({
            "inventory_trigger": trigger
        })
        
        print("✅ Low stock alert processed!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        print(f"Priority: {result.get('priority', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error processing low stock alert: {e}")

def demo_sales_analytics():
    """Demonstrate sales analytics generation"""
    print("\n📊 Generating Sales Analytics...")
    print("=" * 50)
    
    # Create a sales update trigger
    trigger = create_sales_update_trigger("today", 2450.00, 15)
    
    try:
        # Run the agent
        result = sales_monitor_agent.invoke({
            "inventory_trigger": trigger
        })
        
        print("✅ Sales analytics generated!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error generating sales analytics: {e}")

def demo_critical_stock_situation():
    """Demonstrate handling a critical stock situation"""
    print("\n🚨 Simulating Critical Stock Situation...")
    print("=" * 50)
    
    # Create a critical low stock trigger (0 units)
    trigger = create_low_stock_trigger("Wireless Headphones", 0, 50)
    
    try:
        # Run the agent
        result = sales_monitor_agent.invoke({
            "inventory_trigger": trigger
        })
        
        print("✅ Critical situation handled!")
        print(f"Classification: {result.get('classification_decision', 'unknown')}")
        print(f"Priority: {result.get('priority', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error handling critical situation: {e}")

def main():
    """Run all demos"""
    print("🤖 Sales Monitor Agent Demo")
    print("=" * 60)
    print("This demo uses mock data for Zoho Inventory API calls.")
    print("In production, connect to your actual Zoho account.\n")
    
    # Run all demo scenarios
    demo_inventory_check()
    demo_low_stock_alert()
    demo_sales_analytics()
    demo_critical_stock_situation()
    
    print("\n🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Set up Zoho API credentials (see tools/zoho/README.md)")
    print("2. Run setup_zoho.py to configure OAuth")
    print("3. Update environment variables with your tokens")
    print("4. Test with your actual inventory data")

if __name__ == "__main__":
    main() 