"""
Restock and supplier ordering tools for automating purchase orders.
This module provides tools to manage suppliers, create purchase orders, and handle restocking workflows.
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
import uuid
from statistics import mean

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing Zoho client
from .zoho_tools import zoho_client, MOCK_INVENTORY_DATA

# Mock supplier data for development and testing
MOCK_SUPPLIER_DATA = {
    "SUPP001": {
        "supplier_id": "SUPP001",
        "name": "TechVendor Solutions",
        "contact_person": "Sarah Johnson",
        "email": "orders@techvendor.com",
        "phone": "+1-555-0123",
        "category": "Electronics",
        "lead_time_days": 5,
        "minimum_order": 500.00,
        "payment_terms": "Net 30",
        "rating": 4.5,
        "products": ["Wireless Headphones", "Bluetooth Speaker", "USB Cable"],
        "pricing": {
            "Wireless Headphones": {"unit_cost": 65.00, "bulk_discount": 0.1},
            "Bluetooth Speaker": {"unit_cost": 85.00, "bulk_discount": 0.08},
            "USB Cable": {"unit_cost": 8.50, "bulk_discount": 0.15}
        }
    },
    "SUPP002": {
        "supplier_id": "SUPP002", 
        "name": "ElectroMax Wholesale",
        "contact_person": "Mike Chen",
        "email": "purchasing@electromax.com",
        "phone": "+1-555-0456",
        "category": "Electronics",
        "lead_time_days": 7,
        "minimum_order": 1000.00,
        "payment_terms": "Net 45",
        "rating": 4.2,
        "products": ["Wireless Headphones", "Bluetooth Speaker"],
        "pricing": {
            "Wireless Headphones": {"unit_cost": 62.00, "bulk_discount": 0.12},
            "Bluetooth Speaker": {"unit_cost": 82.00, "bulk_discount": 0.10}
        }
    },
    "SUPP003": {
        "supplier_id": "SUPP003",
        "name": "Cable Direct Inc",
        "contact_person": "Lisa Park",
        "email": "orders@cabledirect.com", 
        "phone": "+1-555-0789",
        "category": "Accessories",
        "lead_time_days": 3,
        "minimum_order": 200.00,
        "payment_terms": "Net 15",
        "rating": 4.8,
        "products": ["USB Cable"],
        "pricing": {
            "USB Cable": {"unit_cost": 7.25, "bulk_discount": 0.20}
        }
    }
}

# Mock purchase order tracking
MOCK_PURCHASE_ORDERS = {}

def generate_po_number() -> str:
    """Generate a unique purchase order number."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    return f"PO-{timestamp}-{str(uuid.uuid4())[:8].upper()}"

def calculate_bulk_price(unit_cost: float, quantity: int, bulk_discount: float, min_bulk_qty: int = 50) -> float:
    """Calculate price with bulk discount if applicable."""
    if quantity >= min_bulk_qty:
        return unit_cost * (1 - bulk_discount)
    return unit_cost

@tool
def find_suppliers_tool(item_name: str, required_quantity: int = 1) -> str:
    """Find available suppliers for a specific item with pricing and lead times.
    
    Args:
        item_name: Name of the item to source
        required_quantity: Quantity needed for pricing calculations
    
    Returns:
        String with available suppliers and their details
    """
    try:
        available_suppliers = []
        
        for supplier_id, supplier in MOCK_SUPPLIER_DATA.items():
            if item_name in supplier["products"]:
                pricing_info = supplier["pricing"].get(item_name, {})
                unit_cost = pricing_info.get("unit_cost", 0)
                bulk_discount = pricing_info.get("bulk_discount", 0)
                
                # Calculate final unit price
                final_price = calculate_bulk_price(unit_cost, required_quantity, bulk_discount)
                total_cost = final_price * required_quantity
                
                # Check if meets minimum order
                meets_minimum = total_cost >= supplier["minimum_order"]
                
                supplier_info = {
                    "supplier_id": supplier_id,
                    "name": supplier["name"],
                    "contact": supplier["contact_person"],
                    "email": supplier["email"],
                    "lead_time": supplier["lead_time_days"],
                    "unit_cost": unit_cost,
                    "final_price": final_price,
                    "total_cost": total_cost,
                    "minimum_order": supplier["minimum_order"],
                    "meets_minimum": meets_minimum,
                    "rating": supplier["rating"],
                    "payment_terms": supplier["payment_terms"]
                }
                available_suppliers.append(supplier_info)
        
        if not available_suppliers:
            return f"No suppliers found for '{item_name}'. Consider sourcing from alternative suppliers."
        
        # Sort by price (ascending)
        available_suppliers.sort(key=lambda x: x["final_price"])
        
        result = f"🔍 **Suppliers for {item_name} (Quantity: {required_quantity})**\n\n"
        
        for i, supplier in enumerate(available_suppliers, 1):
            status_icon = "✅" if supplier["meets_minimum"] else "⚠️"
            bulk_info = f" (Bulk price: ${supplier['final_price']:.2f})" if supplier['final_price'] < supplier['unit_cost'] else ""
            
            result += f"{status_icon} **{i}. {supplier['name']}** (Rating: {supplier['rating']}/5)\n"
            result += f"   Contact: {supplier['contact']} ({supplier['email']})\n"
            result += f"   Price: ${supplier['unit_cost']:.2f}/unit{bulk_info}\n"
            result += f"   Total Cost: ${supplier['total_cost']:.2f}\n"
            result += f"   Lead Time: {supplier['lead_time']} days\n"
            result += f"   Payment: {supplier['payment_terms']}\n"
            result += f"   Min Order: ${supplier['minimum_order']:.2f} {'✅ Met' if supplier['meets_minimum'] else '❌ Not Met'}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding suppliers: {e}")
        return f"Error finding suppliers: {str(e)}"

@tool
def create_purchase_order_tool(
    supplier_id: str, 
    item_name: str, 
    quantity: int, 
    delivery_date: str,
    notes: Optional[str] = None
) -> str:
    """Create a purchase order with a specific supplier.
    
    Args:
        supplier_id: ID of the selected supplier
        item_name: Name of the item to order
        quantity: Quantity to order
        delivery_date: Requested delivery date (YYYY-MM-DD)
        notes: Optional order notes
    
    Returns:
        String with purchase order confirmation details
    """
    try:
        # Validate supplier
        if supplier_id not in MOCK_SUPPLIER_DATA:
            return f"Error: Supplier ID '{supplier_id}' not found."
        
        supplier = MOCK_SUPPLIER_DATA[supplier_id]
        
        # Validate item availability
        if item_name not in supplier["products"]:
            return f"Error: Supplier '{supplier['name']}' does not carry '{item_name}'."
        
        # Calculate pricing
        pricing_info = supplier["pricing"].get(item_name, {})
        unit_cost = pricing_info.get("unit_cost", 0)
        bulk_discount = pricing_info.get("bulk_discount", 0)
        
        final_price = calculate_bulk_price(unit_cost, quantity, bulk_discount)
        total_cost = final_price * quantity
        
        # Check minimum order
        if total_cost < supplier["minimum_order"]:
            return f"Error: Order total ${total_cost:.2f} is below minimum order ${supplier['minimum_order']:.2f} for {supplier['name']}."
        
        # Generate PO
        po_number = generate_po_number()
        expected_delivery = datetime.strptime(delivery_date, "%Y-%m-%d")
        order_date = datetime.now()
        
        purchase_order = {
            "po_number": po_number,
            "supplier_id": supplier_id,
            "supplier_name": supplier["name"],
            "supplier_contact": supplier["email"],
            "item_name": item_name,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "final_price": final_price,
            "total_cost": total_cost,
            "order_date": order_date.isoformat(),
            "requested_delivery": delivery_date,
            "expected_delivery": expected_delivery.isoformat(),
            "lead_time_days": supplier["lead_time_days"],
            "payment_terms": supplier["payment_terms"],
            "status": "Pending Approval",
            "notes": notes or "",
            "bulk_discount_applied": final_price < unit_cost
        }
        
        # Store the PO
        MOCK_PURCHASE_ORDERS[po_number] = purchase_order
        
        result = f"📋 **Purchase Order Created Successfully!**\n\n"
        result += f"🆔 **PO Number:** {po_number}\n"
        result += f"🏢 **Supplier:** {supplier['name']}\n"
        result += f"📧 **Contact:** {supplier['contact_person']} ({supplier['email']})\n"
        result += f"📦 **Item:** {item_name}\n"
        result += f"🔢 **Quantity:** {quantity} units\n"
        result += f"💰 **Unit Price:** ${final_price:.2f}"
        
        if purchase_order["bulk_discount_applied"]:
            result += f" (Bulk discount applied: {bulk_discount*100:.0f}% off)\n"
        else:
            result += "\n"
            
        result += f"💵 **Total Cost:** ${total_cost:.2f}\n"
        result += f"📅 **Order Date:** {order_date.strftime('%Y-%m-%d')}\n"
        result += f"🚚 **Requested Delivery:** {delivery_date}\n"
        result += f"⏰ **Lead Time:** {supplier['lead_time_days']} days\n"
        result += f"💳 **Payment Terms:** {supplier['payment_terms']}\n"
        result += f"📊 **Status:** {purchase_order['status']}\n"
        
        if notes:
            result += f"📝 **Notes:** {notes}\n"
        
        result += f"\n✅ **Next Steps:**\n"
        result += f"• PO sent to supplier for confirmation\n"
        result += f"• Awaiting approval workflow completion\n"
        result += f"• Expected confirmation within 24 hours\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating purchase order: {e}")
        return f"Error creating purchase order: {str(e)}"

@tool
def check_order_status_tool(po_number: Optional[str] = None) -> str:
    """Check the status of purchase orders.
    
    Args:
        po_number: Specific PO number to check (optional, checks all if not provided)
    
    Returns:
        String with order status information
    """
    try:
        if not MOCK_PURCHASE_ORDERS:
            return "No purchase orders found in the system."
        
        if po_number:
            if po_number not in MOCK_PURCHASE_ORDERS:
                return f"Purchase order '{po_number}' not found."
            
            orders = {po_number: MOCK_PURCHASE_ORDERS[po_number]}
        else:
            orders = MOCK_PURCHASE_ORDERS
        
        result = f"📊 **Purchase Order Status Report**\n\n"
        
        for po_num, order in orders.items():
            order_date = datetime.fromisoformat(order["order_date"])
            days_since_order = (datetime.now() - order_date).days
            
            result += f"🆔 **PO:** {po_num}\n"
            result += f"🏢 **Supplier:** {order['supplier_name']}\n"
            result += f"📦 **Item:** {order['item_name']} ({order['quantity']} units)\n"
            result += f"💰 **Total:** ${order['total_cost']:.2f}\n"
            result += f"📅 **Ordered:** {order_date.strftime('%Y-%m-%d')} ({days_since_order} days ago)\n"
            result += f"🚚 **Expected Delivery:** {order['requested_delivery']}\n"
            result += f"📊 **Status:** {order['status']}\n"
            
            if order.get("notes"):
                result += f"📝 **Notes:** {order['notes']}\n"
            
            result += "\n"
        
        # Summary stats
        total_orders = len(orders)
        total_value = sum(order["total_cost"] for order in orders.values())
        
        result += f"📈 **Summary:**\n"
        result += f"• Total Orders: {total_orders}\n"
        result += f"• Total Value: ${total_value:.2f}\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking order status: {e}")
        return f"Error checking order status: {str(e)}"

@tool
def approve_purchase_order_tool(po_number: str, approval_notes: Optional[str] = None) -> str:
    """Approve a pending purchase order and send to supplier.
    
    Args:
        po_number: Purchase order number to approve
        approval_notes: Optional approval notes
    
    Returns:
        String confirming order approval and next steps
    """
    try:
        if po_number not in MOCK_PURCHASE_ORDERS:
            return f"Purchase order '{po_number}' not found."
        
        order = MOCK_PURCHASE_ORDERS[po_number]
        
        if order["status"] != "Pending Approval":
            return f"Purchase order '{po_number}' is not pending approval. Current status: {order['status']}"
        
        # Update order status
        order["status"] = "Approved - Sent to Supplier"
        order["approval_date"] = datetime.now().isoformat()
        order["approval_notes"] = approval_notes or ""
        
        # Calculate expected delivery
        order_date = datetime.fromisoformat(order["order_date"])
        expected_delivery = order_date + timedelta(days=order["lead_time_days"])
        order["calculated_delivery"] = expected_delivery.isoformat()
        
        result = f"✅ **Purchase Order Approved!**\n\n"
        result += f"🆔 **PO Number:** {po_number}\n"
        result += f"🏢 **Supplier:** {order['supplier_name']}\n"
        result += f"📦 **Item:** {order['item_name']} ({order['quantity']} units)\n"
        result += f"💰 **Total Cost:** ${order['total_cost']:.2f}\n"
        result += f"📅 **Approval Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        result += f"🚚 **Expected Delivery:** {expected_delivery.strftime('%Y-%m-%d')}\n"
        
        if approval_notes:
            result += f"📝 **Approval Notes:** {approval_notes}\n"
        
        result += f"\n📧 **Actions Taken:**\n"
        result += f"• Purchase order sent to {order['supplier_contact']}\n"
        result += f"• Supplier notification sent\n"
        result += f"• Order tracking initiated\n"
        result += f"• Expected confirmation within 24 hours\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error approving purchase order: {e}")
        return f"Error approving purchase order: {str(e)}"

@tool
def cancel_purchase_order_tool(po_number: str, cancellation_reason: str) -> str:
    """Cancel a purchase order.
    
    Args:
        po_number: Purchase order number to cancel
        cancellation_reason: Reason for cancellation
    
    Returns:
        String confirming order cancellation
    """
    try:
        if po_number not in MOCK_PURCHASE_ORDERS:
            return f"Purchase order '{po_number}' not found."
        
        order = MOCK_PURCHASE_ORDERS[po_number]
        
        if order["status"] in ["Delivered", "Cancelled"]:
            return f"Cannot cancel order '{po_number}'. Current status: {order['status']}"
        
        # Update order status
        old_status = order["status"]
        order["status"] = "Cancelled"
        order["cancellation_date"] = datetime.now().isoformat()
        order["cancellation_reason"] = cancellation_reason
        
        result = f"❌ **Purchase Order Cancelled**\n\n"
        result += f"🆔 **PO Number:** {po_number}\n"
        result += f"🏢 **Supplier:** {order['supplier_name']}\n"
        result += f"📦 **Item:** {order['item_name']} ({order['quantity']} units)\n"
        result += f"💰 **Total Cost:** ${order['total_cost']:.2f}\n"
        result += f"📅 **Previous Status:** {old_status}\n"
        result += f"📅 **Cancelled Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        result += f"📝 **Reason:** {cancellation_reason}\n"
        
        result += f"\n📧 **Actions Taken:**\n"
        result += f"• Cancellation notice sent to {order['supplier_contact']}\n"
        result += f"• Internal teams notified\n"
        result += f"• Order removed from tracking\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error cancelling purchase order: {e}")
        return f"Error cancelling purchase order: {str(e)}"

@tool
def get_supplier_performance_tool(supplier_id: Optional[str] = None) -> str:
    """Get supplier performance metrics and ratings.
    
    Args:
        supplier_id: Specific supplier to analyze (optional, analyzes all if not provided)
    
    Returns:
        String with supplier performance analysis
    """
    try:
        if supplier_id:
            if supplier_id not in MOCK_SUPPLIER_DATA:
                return f"Supplier '{supplier_id}' not found."
            suppliers = {supplier_id: MOCK_SUPPLIER_DATA[supplier_id]}
        else:
            suppliers = MOCK_SUPPLIER_DATA
        
        result = f"📊 **Supplier Performance Report**\n\n"
        
        for sid, supplier in suppliers.items():
            # Calculate metrics based on orders
            supplier_orders = [order for order in MOCK_PURCHASE_ORDERS.values() 
                             if order["supplier_id"] == sid]
            
            total_orders = len(supplier_orders)
            total_value = sum(order["total_cost"] for order in supplier_orders)
            avg_order_value = total_value / total_orders if total_orders > 0 else 0
            
            result += f"🏢 **{supplier['name']}** ({sid})\n"
            result += f"   Rating: {supplier['rating']}/5 ⭐\n"
            result += f"   Category: {supplier['category']}\n"
            result += f"   Lead Time: {supplier['lead_time_days']} days\n"
            result += f"   Payment Terms: {supplier['payment_terms']}\n"
            result += f"   Min Order: ${supplier['minimum_order']:.2f}\n"
            result += f"   Total Orders: {total_orders}\n"
            result += f"   Total Value: ${total_value:.2f}\n"
            result += f"   Avg Order: ${avg_order_value:.2f}\n"
            result += f"   Products: {', '.join(supplier['products'])}\n"
            
            # Performance indicators
            if supplier['rating'] >= 4.5:
                result += f"   Status: ✅ Preferred Supplier\n"
            elif supplier['rating'] >= 4.0:
                result += f"   Status: ✅ Good Supplier\n"
            elif supplier['rating'] >= 3.5:
                result += f"   Status: ⚠️ Average Supplier\n"
            else:
                result += f"   Status: ❌ Below Standard\n"
            
            result += "\n"
        
        # Overall recommendations
        best_supplier = max(suppliers.values(), key=lambda x: x['rating'])
        fastest_supplier = min(suppliers.values(), key=lambda x: x['lead_time_days'])
        
        result += f"🏆 **Recommendations:**\n"
        result += f"• Highest Rated: {best_supplier['name']} ({best_supplier['rating']}/5)\n"
        result += f"• Fastest Delivery: {fastest_supplier['name']} ({fastest_supplier['lead_time_days']} days)\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting supplier performance: {e}")
        return f"Error getting supplier performance: {str(e)}"

@tool
def bulk_restock_tool(restock_list: str, budget_limit: Optional[float] = None) -> str:
    """Create bulk restock orders for multiple items based on demand forecasting.
    
    Args:
        restock_list: JSON string of items to restock with quantities
        budget_limit: Optional budget limit for all orders
    
    Returns:
        String with bulk restock plan and total costs
    """
    try:
        # Parse restock list
        try:
            items = json.loads(restock_list)
        except json.JSONDecodeError:
            return "Error: Invalid JSON format for restock_list. Expected format: [{'item_name': 'Product', 'quantity': 100}, ...]"
        
        if not isinstance(items, list):
            return "Error: restock_list must be a JSON array of items."
        
        total_cost = 0
        restock_plan = []
        errors = []
        
        result = f"📦 **Bulk Restock Analysis**\n\n"
        
        for item in items:
            if not isinstance(item, dict) or 'item_name' not in item or 'quantity' not in item:
                errors.append("Invalid item format - must have 'item_name' and 'quantity'")
                continue
            
            item_name = item['item_name']
            quantity = item['quantity']
            
            # Find best supplier for this item
            best_supplier = None
            best_price = float('inf')
            
            for supplier_id, supplier in MOCK_SUPPLIER_DATA.items():
                if item_name in supplier["products"]:
                    pricing = supplier["pricing"].get(item_name, {})
                    unit_cost = pricing.get("unit_cost", 0)
                    bulk_discount = pricing.get("bulk_discount", 0)
                    
                    final_price = calculate_bulk_price(unit_cost, quantity, bulk_discount)
                    total_item_cost = final_price * quantity
                    
                    if total_item_cost >= supplier["minimum_order"] and final_price < best_price:
                        best_supplier = {
                            "supplier_id": supplier_id,
                            "name": supplier["name"],
                            "unit_cost": unit_cost,
                            "final_price": final_price,
                            "total_cost": total_item_cost,
                            "lead_time": supplier["lead_time_days"]
                        }
                        best_price = final_price
            
            if best_supplier:
                restock_plan.append({
                    "item_name": item_name,
                    "quantity": quantity,
                    "supplier": best_supplier
                })
                total_cost += best_supplier["total_cost"]
            else:
                errors.append(f"No suitable supplier found for {item_name} (quantity: {quantity})")
        
        # Check budget
        within_budget = budget_limit is None or total_cost <= budget_limit
        
        if restock_plan:
            result += f"💰 **Cost Analysis:**\n"
            result += f"Total Cost: ${total_cost:.2f}\n"
            if budget_limit:
                result += f"Budget Limit: ${budget_limit:.2f}\n"
                result += f"Status: {'✅ Within Budget' if within_budget else '❌ Over Budget'}\n"
            result += "\n"
            
            result += f"📋 **Restock Plan:**\n"
            for plan in restock_plan:
                supplier = plan["supplier"]
                result += f"• **{plan['item_name']}** ({plan['quantity']} units)\n"
                result += f"  Supplier: {supplier['name']}\n"
                result += f"  Price: ${supplier['final_price']:.2f}/unit\n"
                result += f"  Total: ${supplier['total_cost']:.2f}\n"
                result += f"  Lead Time: {supplier['lead_time']} days\n\n"
        
        if errors:
            result += f"⚠️ **Issues Found:**\n"
            for error in errors:
                result += f"• {error}\n"
            result += "\n"
        
        if restock_plan and within_budget:
            result += f"✅ **Ready to Proceed:**\n"
            result += f"• {len(restock_plan)} items ready for ordering\n"
            result += f"• Total investment: ${total_cost:.2f}\n"
            result += f"• Use create_purchase_order_tool for each item\n"
        elif restock_plan and not within_budget:
            result += f"⚠️ **Budget Exceeded:**\n"
            result += f"• Consider reducing quantities or removing items\n"
            result += f"• Over budget by: ${total_cost - budget_limit:.2f}\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk restock analysis: {e}")
        return f"Error in bulk restock analysis: {str(e)}"

# Export all tools for easy importing
__all__ = [
    "find_suppliers_tool",
    "create_purchase_order_tool",
    "check_order_status_tool",
    "approve_purchase_order_tool",
    "cancel_purchase_order_tool",
    "get_supplier_performance_tool",
    "bulk_restock_tool"
] 