# Agents from Scratch

This repository contains implementations of LangGraph agents for various business use cases, including email assistance, sales monitoring, and demand forecasting.

## Features

- **Email Assistant**: Intelligent email management with Gmail integration
- **Sales Monitor Agent**: Zoho Inventory integration for sales tracking and inventory management  
- **Demand Forecast Agent**: Advanced demand forecasting with predictive analytics
- **Restock Trigger Agent**: Automated supplier ordering and procurement management (NEW!)

### Demand Forecast Agent

The Demand Forecast Agent is a sophisticated forecasting system that predicts future demand based on inventory changes in Zoho. It uses the same human-in-the-loop and memory architecture as the email assistant template.

#### Key Capabilities:
- **Multi-method Forecasting**: Moving average, exponential smoothing, and hybrid approaches
- **Stockout Risk Analysis**: Early warning system for inventory shortages
- **Seasonal Pattern Detection**: Automatic identification of seasonal demand cycles
- **Intelligent Reorder Recommendations**: Cost-optimized purchase suggestions
- **Human-in-the-Loop**: Approval workflows for critical forecasting decisions
- **Memory Learning**: Adapts forecasting methods based on accuracy and user preferences

#### Forecasting Tools:
- `analyze_demand_patterns_tool`: Historical demand pattern analysis
- `forecast_demand_tool`: Future demand prediction with multiple methods
- `analyze_stockout_risk_tool`: Risk assessment across all inventory items
- `generate_reorder_recommendations_tool`: Intelligent purchase planning
- `seasonal_demand_analysis_tool`: Seasonal trend analysis and insights

#### Usage Example:
```python
from src.email_assistant.demand_forecast_agent_hitl_memory import demand_forecast_agent
from src.email_assistant.demand_forecast_utils import create_stockout_risk_trigger

# Create a stockout risk trigger
trigger = create_stockout_risk_trigger(
    item_name="USB Cable",
    current_stock=5,
    daily_sales_rate=15.2
)

# Run forecasting analysis
result = demand_forecast_agent.invoke({
    "forecast_trigger": trigger
})
```

See `examples/demand_forecast_example.py` for comprehensive usage examples.

### Restock Trigger Agent

The Restock Trigger Agent automates supplier ordering and procurement workflows, managing the entire purchase order lifecycle from supplier research to order fulfillment. It uses the same human-in-the-loop and memory architecture as the other agents.

#### Key Capabilities:
- **Automated Supplier Sourcing**: Research and compare suppliers with pricing, lead times, and ratings
- **Purchase Order Management**: Create, approve, track, and manage purchase orders end-to-end
- **Cost Optimization**: Bulk pricing calculations, supplier comparison, and budget management
- **Supplier Performance Tracking**: Monitor delivery rates, quality metrics, and relationship history
- **Human-in-the-Loop**: Approval workflows for large orders and critical procurement decisions
- **Memory Learning**: Adapts supplier selection and approval thresholds based on past performance

#### Procurement Tools:
- `find_suppliers_tool`: Research suppliers with pricing and lead times
- `create_purchase_order_tool`: Generate purchase orders with selected suppliers
- `check_order_status_tool`: Track purchase order progress and delivery
- `approve_purchase_order_tool`: Approve orders and send to suppliers
- `cancel_purchase_order_tool`: Cancel orders with proper notifications
- `get_supplier_performance_tool`: Evaluate supplier metrics and ratings
- `bulk_restock_tool`: Plan and cost-optimize multiple item orders

#### Usage Example:
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

# Run procurement automation
result = restock_trigger_agent.invoke({
    "restock_trigger": trigger
})
```

See `examples/restock_trigger_example.py` for comprehensive usage examples.

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables for API integrations (Zoho, Gmail, etc.)
4. Run examples to test functionality

## Architecture

All agents follow a consistent pattern:
- **Triage System**: Classifies and routes incoming requests
- **Human-in-the-Loop**: Critical decision approval workflows
- **Memory System**: Learns from user interactions and preferences
- **Tool Integration**: Modular tools for specific business functions

## Contributing

Feel free to contribute additional agents, tools, or improvements following the established patterns. 



