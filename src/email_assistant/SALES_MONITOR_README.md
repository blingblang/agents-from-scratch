# Sales Monitor Agent - Zoho Inventory Integration

A sophisticated sales monitoring and inventory management agent built using LangGraph, inspired by the email assistant architecture. This agent monitors Zoho Inventory accounts, provides intelligent alerts, and automates inventory management tasks with human-in-the-loop capabilities and memory.

## Overview

The Sales Monitor Agent is designed to:
- **Monitor inventory levels** and provide proactive alerts
- **Track sales performance** and identify trends
- **Automate inventory management** tasks with approval workflows
- **Learn from user preferences** and adapt over time
- **Integrate with Zoho Inventory** API for real-time data

## Architecture

The agent follows the same pattern as the email assistant with these components:

### 1. **Triage System**
- Analyzes inventory triggers (low stock, sales updates, manual checks)
- Classifies urgency: `monitor`, `alert`, `action_required`
- Routes to appropriate handling based on priority

### 2. **Agent with Tools**
- **fetch_inventory_tool**: Get current inventory status
- **check_stock_levels_tool**: Check stock levels and alerts
- **get_sales_analytics_tool**: Retrieve sales performance data
- **create_order_tool**: Create new sales orders
- **update_inventory_tool**: Update inventory quantities
- **Question**: Ask for human input/approval
- **Done**: Complete the task

### 3. **Human-in-the-Loop (HITL)**
- Approval workflows for critical actions (large orders, inventory changes)
- Questions when business context is unclear
- Configurable approval thresholds

### 4. **Memory System**
- Learns user preferences and approval patterns
- Adapts business rules based on past interactions
- Remembers seasonal patterns and risk tolerance

## Files Created

```
src/email_assistant/
├── tools/zoho/
│   ├── __init__.py                    # Zoho tools module exports
│   ├── zoho_tools.py                  # Main Zoho Inventory API tools
│   ├── prompt_templates.py           # Tool descriptions for prompts
│   ├── setup_zoho.py                 # OAuth setup script
│   └── README.md                     # Zoho tools documentation
├── inventory_schemas.py               # Pydantic schemas for inventory state
├── inventory_prompts.py               # Agent prompts and instructions
├── inventory_utils.py                 # Utility functions
├── sales_monitor_agent_hitl_memory.py # Main agent implementation
└── SALES_MONITOR_README.md           # This documentation
```

## Setup Instructions

### 1. Install Dependencies

The agent uses the existing project dependencies plus requests for API calls:

```bash
pip install requests
```

### 2. Zoho API Setup

Follow the setup guide in `src/email_assistant/tools/zoho/README.md`:

1. Create a Zoho Developer Account at [Zoho API Console](https://api-console.zoho.com/)
2. Create a "Self Client" application
3. Add credentials to your `.env` file:



### 3. Run OAuth Setup

```bash
python src/email_assistant/tools/zoho/setup_zoho.py
```

This will guide you through the OAuth flow and save your tokens.

## Usage Examples

### Basic Inventory Check

```python
from src.email_assistant.sales_monitor_agent_hitl_memory import sales_monitor_agent
from src.email_assistant.inventory_utils import create_manual_check_trigger

# Create a manual check trigger
trigger = create_manual_check_trigger("manager", "general")

# Run the agent
result = sales_monitor_agent.invoke({
    "inventory_trigger": trigger
})

print("Agent response:", result)
```

### Low Stock Alert

```python
from src.email_assistant.inventory_utils import create_low_stock_trigger

# Create a low stock trigger for a specific item
trigger = create_low_stock_trigger("USB Cable", 5, 25)

# Run the agent
result = sales_monitor_agent.invoke({
    "inventory_trigger": trigger
})
```

### Sales Analytics Report

```python
from src.email_assistant.inventory_utils import create_sales_update_trigger

# Create a sales update trigger
trigger = create_sales_update_trigger("today", 2450.00, 15)

# Run the agent
result = sales_monitor_agent.invoke({
    "inventory_trigger": trigger
})
```

## Agent Capabilities

### 🔍 **Inventory Monitoring**
- Real-time stock level tracking
- Automated low stock alerts
- Multi-category inventory overview
- Stock health assessment

### 📊 **Sales Analytics**
- Daily, weekly, monthly sales reports
- Top-selling items identification
- Revenue and order tracking
- Trend analysis and insights

### ⚡ **Automated Actions**
- Intelligent reorder suggestions
- Automatic order creation (with approval)
- Inventory quantity adjustments
- Stock optimization recommendations

### 🤝 **Human-in-the-Loop**
- Configurable approval workflows
- Business rule customization
- Risk management controls
- Manual oversight for critical decisions

### 🧠 **Memory & Learning**
- User preference adaptation
- Historical pattern recognition
- Seasonal trend awareness
- Continuous improvement

## Configuration

### Approval Thresholds

The agent includes configurable thresholds for human approval:

- **Order Creation**: Orders over $500 require approval
- **Inventory Updates**: Changes over 25 units require approval
- **Critical Actions**: All stockout situations require notification

### Business Rules

Default business rules can be customized:

- **Reorder Levels**: Configurable per item category
- **Safety Stock**: 2 weeks of average sales
- **Lead Times**: 7 days default, configurable per supplier

## Mock Data for Development

The agent includes comprehensive mock data for development and testing:

- **Sample Inventory**: Electronics and accessories with realistic stock levels
- **Sales Data**: Daily sales, orders, and top-selling items
- **Low Stock Alerts**: Pre-configured alerts for testing

## Integration with LangGraph Studio

The agent is fully compatible with LangGraph Studio for:
- Visual workflow debugging
- State inspection and modification
- Tool call monitoring
- Performance analysis

## Deployment Options

The agent can be deployed in several ways:

1. **Standalone Script**: Run as needed for manual checks
2. **Scheduled Jobs**: Automated daily/hourly monitoring
3. **Webhook Integration**: Real-time triggers from Zoho
4. **LangGraph Platform**: Full cloud deployment with UI

## Extending the Agent

The modular architecture makes it easy to extend:

### Adding New Tools
1. Create new tool functions in `zoho_tools.py`
2. Update prompt templates
3. Add to tool loading in `base.py`

### Custom Triggers
1. Define new trigger types in `inventory_schemas.py`
2. Add parsing logic in `inventory_utils.py`
3. Update triage logic for new scenarios

### Enhanced Memory
1. Integrate LangMem for advanced memory management
2. Add domain-specific memory tools
3. Implement collaborative memory sharing

## Testing

The agent includes comprehensive testing capabilities:

- **Mock API responses** for offline development
- **Unit tests** for individual tools
- **Integration tests** for full workflows
- **LangSmith tracking** for evaluation

## Troubleshooting

### Common Issues

1. **API Authentication**: Check token expiration and refresh
2. **Organization ID**: Verify correct Zoho organization
3. **Rate Limits**: Implement backoff for API calls
4. **Memory Storage**: Ensure proper store configuration

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

Planned improvements include:

- **Multi-warehouse support**: Track inventory across locations
- **Supplier integration**: Automated purchase order generation
- **Demand forecasting**: ML-powered inventory planning
- **Mobile notifications**: Real-time alerts on mobile devices
- **Dashboard integration**: Visual inventory dashboards

---

## Questions or Issues?

For questions about the Sales Monitor Agent:
1. Check the Zoho tools README for API setup
2. Review the mock data for expected formats
3. Use LangGraph Studio for debugging workflows
4. Enable debug logging for detailed troubleshooting 