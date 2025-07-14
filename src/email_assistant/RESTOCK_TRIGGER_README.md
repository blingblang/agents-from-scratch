# Restock Trigger Agent - Automated Supplier Ordering

A sophisticated procurement automation agent built using LangGraph, following the same architecture as the email assistant. This agent manages supplier relationships, automates purchase order workflows, and ensures optimal inventory replenishment through intelligent supplier selection and cost optimization.

## Overview

The Restock Trigger Agent is designed to:
- **Automate supplier sourcing** and purchase order creation
- **Optimize procurement costs** through intelligent supplier selection
- **Manage supplier relationships** and performance tracking
- **Handle approval workflows** for large orders and critical decisions
- **Learn from procurement patterns** and adapt to business preferences
- **Integrate with Zoho Inventory** for seamless inventory management

## Architecture

The agent follows the same pattern as the email assistant with these components:

### 1. **Triage System**
- Analyzes restock triggers (stockout alerts, reorder requests, seasonal prep)
- Classifies urgency: `monitor`, `alert`, `action_required`
- Routes to appropriate procurement handling based on business impact

### 2. **Agent with Procurement Tools**
- **find_suppliers_tool**: Research suppliers with pricing and lead times
- **create_purchase_order_tool**: Generate purchase orders with selected suppliers
- **check_order_status_tool**: Track purchase order progress and delivery
- **approve_purchase_order_tool**: Approve orders and send to suppliers
- **cancel_purchase_order_tool**: Cancel orders with proper notifications
- **get_supplier_performance_tool**: Evaluate supplier metrics and ratings
- **bulk_restock_tool**: Plan and cost-optimize multiple item orders
- **Question**: Ask for approval or business input
- **Done**: Complete the procurement task

### 3. **Human-in-the-Loop (HITL)**
- Approval workflows for orders over $1000
- Supplier selection confirmation for critical items
- Budget validation for large procurement activities
- Emergency order authorization

### 4. **Memory System**
- Learns supplier performance and reliability patterns
- Adapts approval thresholds based on user preferences
- Remembers cost optimization strategies and bulk ordering patterns
- Improves supplier selection based on past success rates

## Files Created

```
src/email_assistant/
├── restock_agent_hitl_memory.py         # Main agent implementation
├── restock_prompts.py                   # Procurement-specific prompts
├── restock_schemas.py                   # Data structures and state
├── restock_utils.py                     # Utility functions
├── tools/zoho/
│   ├── restock_tools.py                 # Supplier and ordering tools
│   └── prompt_templates.py             # Updated with restock tools
examples/
├── restock_trigger_example.py          # Usage examples
```

## Key Features

### 🏢 **Supplier Management**
- **Multi-supplier Research**: Compare pricing, lead times, and reliability
- **Performance Tracking**: Monitor delivery rates and quality metrics
- **Relationship Management**: Maintain communication and preference history
- **Backup Sourcing**: Alternative suppliers for risk mitigation

### 💰 **Cost Optimization**
- **Bulk Pricing**: Automatic bulk discount calculations
- **Supplier Comparison**: Best price and value analysis
- **Budget Management**: Cost tracking and budget compliance
- **Promotional Opportunities**: Leverage supplier discounts and promotions

### 📋 **Purchase Order Management**
- **Automated PO Creation**: Generate orders with proper specifications
- **Approval Workflows**: Human oversight for large or critical orders
- **Order Tracking**: Real-time status monitoring and delivery updates
- **Order Modifications**: Cancel, edit, or expedite orders as needed

### 🤝 **Human Collaboration**
- **Approval Thresholds**: Configurable limits for autonomous ordering
- **Supplier Selection**: Confirm choices for critical or new suppliers
- **Budget Authorization**: Validate spending against budget constraints
- **Emergency Procedures**: Fast-track critical orders with proper oversight

### 🧠 **Memory & Learning**
- **Supplier Performance**: Learn which suppliers deliver consistently
- **Cost Patterns**: Identify best pricing and bulk order strategies
- **Approval Behavior**: Adapt to user's risk tolerance and preferences
- **Seasonal Trends**: Remember seasonal supplier performance variations

## Usage Examples

### Basic Stockout Alert Processing

```python
from src.email_assistant.restock_agent_hitl_memory import restock_trigger_agent
from src.email_assistant.restock_utils import create_stockout_alert_trigger

# Create a critical stockout alert
trigger = create_stockout_alert_trigger(
    item_name="USB Cable",
    current_stock=2,
    reorder_level=25,
    daily_consumption=15.2
)

# Run the agent
result = restock_trigger_agent.invoke({
    "restock_trigger": trigger
})
```

### Supplier Sourcing and Ordering

```python
from src.email_assistant.restock_utils import create_reorder_request_trigger

# Create a reorder request for multiple items
trigger = create_reorder_request_trigger(
    item_names=["Wireless Headphones", "Bluetooth Speaker"],
    quantities={"Wireless Headphones": 100, "Bluetooth Speaker": 75},
    budget_limit=15000.00
)

# Run the agent
result = restock_trigger_agent.invoke({
    "restock_trigger": trigger
})
```

### Emergency Order Processing

```python
from src.email_assistant.restock_utils import create_emergency_order_trigger

# Create an emergency order trigger
trigger = create_emergency_order_trigger(
    item_name="Critical Component",
    urgent_quantity=50,
    max_budget=5000.00,
    delivery_deadline="2025-01-20"
)

# Run the agent
result = restock_trigger_agent.invoke({
    "restock_trigger": trigger
})
```

### Seasonal Preparation

```python
from src.email_assistant.restock_utils import create_seasonal_prep_trigger

# Prepare for seasonal demand
trigger = create_seasonal_prep_trigger(
    season="holiday",
    item_categories=["Electronics", "Accessories"],
    lead_time_buffer=45
)

# Run the agent
result = restock_trigger_agent.invoke({
    "restock_trigger": trigger
})
```

## Agent Capabilities

### 🔍 **Supplier Research**
- Automated supplier discovery and qualification
- Pricing comparison and negotiation support
- Lead time and reliability assessment
- Risk evaluation and backup planning

### ⚡ **Automated Ordering**
- Purchase order generation with proper specifications
- Supplier communication and order confirmation
- Delivery tracking and exception handling
- Invoice and payment coordination

### 📊 **Performance Analytics**
- Supplier performance dashboards
- Cost savings tracking and reporting
- Order accuracy and delivery metrics
- Procurement efficiency analytics

### 🎯 **Risk Management**
- Supplier diversification strategies
- Lead time buffer management
- Quality and reliability monitoring
- Emergency sourcing procedures

## Configuration

### Approval Thresholds

The agent includes configurable thresholds for human approval:

- **Purchase Orders**: Orders over $1000 require approval
- **Emergency Orders**: All urgent orders require authorization
- **New Suppliers**: First-time supplier orders need confirmation
- **Budget Limits**: Orders approaching budget limits trigger review

### Business Rules

Default business rules can be customized:

- **Supplier Selection**: Prefer reliable suppliers with good ratings
- **Cost Optimization**: Balance cost savings with delivery reliability
- **Lead Times**: Factor in buffer time for critical items
- **Payment Terms**: Negotiate favorable payment schedules

## Integration with Existing Systems

The agent integrates seamlessly with:

- **Zoho Inventory**: Real-time stock monitoring and updates
- **Demand Forecast Agent**: Coordinate forecasting with procurement
- **Existing Suppliers**: Leverage current supplier relationships
- **Budget Systems**: Align procurement with financial planning

## Mock Data and Development

For development and testing, the agent includes:

- **Mock Supplier Database**: 3 sample suppliers with different specialties
- **Sample Purchase Orders**: Example order workflows and status tracking
- **Pricing Models**: Bulk discount calculations and cost optimization
- **Performance Metrics**: Simulated supplier performance data

### Sample Suppliers

1. **TechVendor Solutions** (Electronics, 5-day lead time, 4.5/5 rating)
2. **ElectroMax Wholesale** (Electronics, 7-day lead time, 4.2/5 rating)
3. **Cable Direct Inc** (Accessories, 3-day lead time, 4.8/5 rating)

## Performance and Optimization

### Cost Savings Metrics
- Bulk discount utilization
- Supplier price comparison savings
- Emergency order cost avoidance
- Payment term optimization

### Efficiency Metrics
- Order processing time
- Supplier response rates
- Delivery accuracy
- Procurement cycle time

## Error Handling

The agent includes robust error handling:
- Graceful fallback when suppliers are unavailable
- Alternative sourcing for failed orders
- Budget validation and constraint management
- Detailed error logging and troubleshooting

## Security and Compliance

- Secure supplier communication protocols
- Purchase order audit trails
- Budget authorization workflows
- Sensitive data protection

## Testing and Validation

Run the test examples to verify functionality:

```bash
python examples/restock_trigger_example.py
```

Test specific scenarios:
- Stockout alert processing
- Supplier comparison and selection
- Purchase order creation and approval
- Emergency order handling

## Future Enhancements

Planned improvements include:

- **Supplier API Integration**: Direct integration with supplier systems
- **Contract Management**: Automated contract compliance and renewal
- **Advanced Analytics**: Machine learning for demand-supply optimization
- **Mobile Approvals**: Mobile app integration for approval workflows
- **Global Sourcing**: Multi-region supplier network management
- **Sustainability Metrics**: Environmental impact tracking

---

## Questions or Issues?

For questions about the Restock Trigger Agent:
1. Check the examples for usage patterns
2. Review supplier tool documentation for API setup
3. Test with mock data for development
4. Use LangGraph Studio for debugging workflows
5. Enable debug logging for detailed troubleshooting

---

## Integration with Other Agents

The Restock Trigger Agent works seamlessly with:

- **Demand Forecast Agent**: Uses forecasting data to optimize order timing and quantities
- **Sales Monitor Agent**: Responds to sales trends and inventory alerts
- **Email Assistant**: Can be triggered by email notifications from suppliers

This creates a comprehensive inventory management ecosystem that handles forecasting, monitoring, and procurement automatically while maintaining human oversight for critical decisions. 