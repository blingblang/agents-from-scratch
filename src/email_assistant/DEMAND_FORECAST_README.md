# Demand Forecast Agent - Zoho Inventory Integration

A sophisticated demand forecasting agent built using LangGraph, following the same architecture as the email assistant. This agent monitors Zoho Inventory accounts, analyzes demand patterns, predicts future inventory needs, and provides intelligent recommendations with human-in-the-loop capabilities and memory.

## Overview

The Demand Forecast Agent is designed to:
- **Analyze demand patterns** using historical sales data and trends
- **Predict future demand** using multiple forecasting methods
- **Assess stockout risks** and provide early warning alerts
- **Generate reorder recommendations** with cost optimization
- **Learn from user preferences** and adapt forecasting methods over time
- **Integrate with Zoho Inventory** API for real-time data access

## Architecture

The agent follows the same pattern as the email assistant with these components:

### 1. **Triage System**
- Analyzes forecasting triggers (stockout risk, forecast requests, seasonal analysis)
- Classifies urgency: `monitor`, `alert`, `action_required`
- Routes to appropriate handling based on business impact

### 2. **Agent with Forecasting Tools**
- **analyze_demand_patterns_tool**: Historical demand pattern analysis
- **forecast_demand_tool**: Multi-method demand prediction
- **analyze_stockout_risk_tool**: Risk assessment across inventory
- **generate_reorder_recommendations_tool**: Intelligent purchase planning
- **seasonal_demand_analysis_tool**: Seasonal trend analysis
- **Question**: Ask for human input/clarification
- **Done**: Complete the forecasting task

### 3. **Human-in-the-Loop (HITL)**
- Approval workflows for large order recommendations
- Questions when forecast confidence is low
- User confirmation for critical forecasting decisions

### 4. **Memory System**
- Learns forecasting method accuracy for different items
- Adapts business rules based on past interactions
- Remembers seasonal patterns and user preferences
- Improves forecast accuracy over time

## Files Created

```
src/email_assistant/
├── demand_forecast_agent_hitl_memory.py    # Main agent implementation
├── demand_forecast_prompts.py              # Forecasting-specific prompts
├── demand_forecast_schemas.py              # Data structures and state
├── demand_forecast_utils.py                # Utility functions
├── tools/zoho/
│   ├── demand_forecast_tools.py            # Forecasting tools implementation
│   └── prompt_templates.py                # Updated with forecast tools
examples/
├── demand_forecast_example.py              # Usage examples
└── test_demand_forecast.py                 # Basic functionality test
```

## Key Features

### 🔮 **Multi-Method Forecasting**
- **Moving Average**: Simple trend following
- **Exponential Smoothing**: Weighted recent data
- **Hybrid**: Combines multiple methods for accuracy
- **Seasonal Adjustments**: Accounts for cyclical patterns

### 📊 **Demand Pattern Analysis**
- Historical trend identification
- Volatility and stability metrics
- Seasonal factor calculations
- Forecast accuracy tracking

### ⚠️ **Stockout Risk Assessment**
- Real-time risk evaluation
- Days-until-stockout calculations
- Priority-based alerting system
- Critical situation identification

### 💡 **Intelligent Recommendations**
- Cost-optimized reorder quantities
- Lead time considerations
- Safety stock calculations
- Urgency-based prioritization

### 🧠 **Memory & Learning**
- Forecasting method performance tracking
- User preference adaptation
- Business rule customization
- Continuous accuracy improvement

## Usage Examples

### Basic Stockout Risk Analysis

```python
from src.email_assistant.demand_forecast_agent_hitl_memory import demand_forecast_agent
from src.email_assistant.demand_forecast_utils import create_stockout_risk_trigger

# Create a stockout risk trigger for critical item
trigger = create_stockout_risk_trigger(
    item_name="USB Cable",
    current_stock=5,
    daily_sales_rate=15.2
)

# Run the agent
result = demand_forecast_agent.invoke({
    "forecast_trigger": trigger
})
```

### Demand Forecasting Request

```python
from src.email_assistant.demand_forecast_utils import create_forecast_request_trigger

# Create a forecast request for specific items
trigger = create_forecast_request_trigger(
    item_names=["Wireless Headphones", "Bluetooth Speaker"],
    forecast_days=14,
    method="hybrid"
)

# Run the agent
result = demand_forecast_agent.invoke({
    "forecast_trigger": trigger
})
```

### Seasonal Analysis

```python
from src.email_assistant.demand_forecast_utils import create_seasonal_analysis_trigger

# Create a seasonal analysis trigger
trigger = create_seasonal_analysis_trigger(
    item_names=["All Electronics"]
)

# Run the agent
result = demand_forecast_agent.invoke({
    "forecast_trigger": trigger
})
```

### Reorder Planning

```python
from src.email_assistant.demand_forecast_utils import create_reorder_planning_trigger

# Create a reorder planning trigger
trigger = create_reorder_planning_trigger(
    lead_time_days=7,
    safety_stock_days=14
)

# Run the agent
result = demand_forecast_agent.invoke({
    "forecast_trigger": trigger
})
```

## Agent Capabilities

### 📈 **Forecasting Methods**
- Multiple algorithms for different item types
- Confidence level calculations
- Accuracy tracking and improvement
- Method selection based on historical performance

### 🎯 **Risk Management**
- Early warning systems
- Criticality assessment
- Business impact evaluation
- Contingency planning

### 📋 **Purchase Planning**
- Optimal order quantities
- Cost-benefit analysis
- Supplier lead time integration
- Budget consideration

### 🤝 **Human Collaboration**
- Transparent decision making
- User preference learning
- Business rule adaptation
- Feedback incorporation

## Configuration

### Forecasting Parameters

The agent includes configurable parameters for:

- **Forecast Horizons**: 7, 14, 30, 90 days
- **Confidence Thresholds**: Minimum 70% for automatic decisions
- **Risk Levels**: Critical (<3 days), High (<7 days), Medium (<14 days)
- **Approval Thresholds**: Orders over $1000 require approval

### Business Rules

Default business rules can be customized:

- **Safety Stock Levels**: 14 days of average demand
- **Reorder Points**: Lead time + safety stock
- **Seasonal Adjustments**: Automatic pattern detection
- **Method Selection**: Performance-based algorithm choice

## Integration with Zoho Inventory

The agent integrates seamlessly with existing Zoho Inventory tools:

- Uses same authentication and API client
- Leverages existing mock data for development
- Compatible with real Zoho API when configured
- Extends current inventory monitoring capabilities

## Performance and Accuracy

### Forecasting Accuracy Metrics
- Mean Absolute Error (MAE)
- Mean Absolute Percentage Error (MAPE) 
- Forecast bias tracking
- Method comparison analytics

### Continuous Improvement
- Learn from actual vs. predicted outcomes
- Adjust parameters based on performance
- User feedback integration
- Seasonal pattern refinement

## Error Handling

The agent includes robust error handling:
- Graceful fallback to alternative forecasting methods
- Mock data when API is unavailable
- Detailed error logging and troubleshooting
- User-friendly error messages

## Security and Privacy

- Environment variable configuration for API keys
- No sensitive data logging
- Secure memory storage patterns
- Audit trail for critical decisions

## Testing and Validation

Run the test script to verify functionality:

```bash
python test_demand_forecast.py
```

Run comprehensive examples:

```bash
python examples/demand_forecast_example.py
```

## Future Enhancements

Planned improvements include:

- **Machine Learning Integration**: Advanced ML-based forecasting
- **Multi-location Support**: Warehouse-specific forecasting
- **Supplier Integration**: Direct purchase order generation
- **Dashboard Visualization**: Real-time forecasting dashboards
- **External Data Sources**: Weather, market trends, promotions
- **Mobile Notifications**: Real-time alerts on mobile devices

---

## Questions or Issues?

For questions about the Demand Forecast Agent:
1. Check the test script for basic functionality verification
2. Review the examples for usage patterns
3. Check Zoho tools README for API setup
4. Use LangGraph Studio for debugging workflows
5. Enable debug logging for detailed troubleshooting 