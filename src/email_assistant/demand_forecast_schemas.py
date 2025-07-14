from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict, Literal, Annotated
from langgraph.graph import MessagesState

class DemandForecastRouterSchema(BaseModel):
    """Analyze demand forecasting requests and route them according to their urgency and type."""

    reasoning: str = Field(
        description="Step-by-step reasoning behind the classification."
    )
    classification: Literal["monitor", "alert", "action_required"] = Field(
        description="The classification of demand forecasting situation: 'monitor' for routine analysis, "
        "'alert' for trends needing attention but not urgent, "
        "'action_required' for critical forecasting situations requiring immediate action",
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Priority level of the forecasting request"
    )

class DemandForecastStateInput(TypedDict):
    # This is the input to the state for demand forecasting
    forecast_trigger: Dict[str, Any]  # Could be stockout risk, forecast request, etc.

class DemandForecastState(MessagesState):
    # This state class has the messages key built in from MessagesState
    forecast_trigger: Dict[str, Any]
    classification_decision: Literal["monitor", "alert", "action_required"]
    priority: Literal["low", "medium", "high", "critical"]

class ForecastRequest(TypedDict):
    item_name: Optional[str]
    forecast_days: int
    method: Literal["moving_average", "exponential", "hybrid", "seasonal"]
    confidence_level: float

class DemandForecast(TypedDict):
    item_name: str
    forecast_period: int  # days
    daily_forecasts: List[float]
    total_forecast: float
    confidence_level: float
    method_used: str
    seasonal_factor: float
    trend_factor: float
    stockout_risk_days: int

class StockoutRisk(TypedDict):
    item_name: str
    current_stock: int
    days_until_stockout: int
    daily_consumption_rate: float
    risk_level: Literal["low", "medium", "high", "critical"]
    recommended_action: str

class ReorderRecommendation(TypedDict):
    item_name: str
    current_stock: int
    recommended_quantity: int
    total_cost: float
    urgency: Literal["low", "medium", "high", "urgent"]
    expected_stockout_date: str
    lead_time_days: int
    safety_stock_days: int

class SeasonalPattern(TypedDict):
    item_name: str
    peak_season: str
    low_season: str
    seasonal_variance: float  # percentage
    current_seasonal_factor: float
    recommendations: List[str]

class DemandAnalysis(TypedDict):
    item_name: str
    analysis_period: int  # days
    average_daily_demand: float
    trend_direction: Literal["increasing", "decreasing", "stable"]
    trend_factor: float
    volatility_percentage: float
    seasonal_factor: float
    current_stock: int
    forecasting_accuracy: Optional[float]

class ForecastTrigger(BaseModel):
    """Represents different types of triggers that can initiate demand forecasting"""
    
    trigger_type: Literal["stockout_risk", "forecast_request", "pattern_analysis", "seasonal_analysis", "reorder_planning", "accuracy_review"] = Field(
        description="Type of trigger that initiated the forecasting"
    )
    triggered_by: Optional[str] = Field(
        description="What or who triggered this forecast request"
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Priority level of this forecast request"
    )
    details: Dict[str, Any] = Field(
        description="Additional details about the forecast trigger"
    )
    item_scope: Optional[List[str]] = Field(
        description="Specific items to focus on (if any)"
    )
    forecast_horizon: Optional[int] = Field(
        description="Number of days to forecast ahead"
    )

class ForecastAccuracy(TypedDict):
    method: str
    item_name: str
    forecast_value: float
    actual_value: float
    accuracy_percentage: float
    absolute_error: float
    date_evaluated: str

class InventoryOptimization(TypedDict):
    item_name: str
    current_reorder_level: int
    recommended_reorder_level: int
    current_safety_stock: int
    recommended_safety_stock: int
    optimization_reasoning: str
    expected_service_level: float

class DemandForecastMetrics(TypedDict):
    total_items_analyzed: int
    average_forecast_accuracy: float
    high_risk_items: int
    medium_risk_items: int
    total_reorder_value: float
    forecast_confidence: float
    methodology_performance: Dict[str, float]  # method name -> accuracy

class BusinessScenario(TypedDict):
    scenario_name: str
    description: str
    demand_multiplier: float  # factor to adjust base forecasts
    affected_categories: List[str]
    duration_days: int
    confidence_level: float 