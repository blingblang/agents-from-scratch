from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict, Literal, Annotated
from langgraph.graph import MessagesState

class InventoryRouterSchema(BaseModel):
    """Analyze inventory data and route it according to its urgency and type."""

    reasoning: str = Field(
        description="Step-by-step reasoning behind the classification."
    )
    classification: Literal["monitor", "alert", "action_required"] = Field(
        description="The classification of inventory situation: 'monitor' for normal status, "
        "'alert' for items needing attention but not urgent, "
        "'action_required' for critical situations requiring immediate action",
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Priority level of the situation"
    )

class InventoryStateInput(TypedDict):
    # This is the input to the state for inventory monitoring
    inventory_trigger: Dict[str, Any]  # Could be low stock alert, sales update, etc.

class InventoryState(MessagesState):
    # This state class has the messages key built in from MessagesState
    inventory_trigger: Dict[str, Any]
    classification_decision: Literal["monitor", "alert", "action_required"]
    priority: Literal["low", "medium", "high", "critical"]

class InventoryItem(TypedDict):
    item_id: str
    item_name: str
    sku: str
    quantity_available: int
    quantity_committed: int
    reorder_level: int
    unit_price: float
    category: str
    last_updated: str

class StockAlert(TypedDict):
    item_name: str
    current_stock: int
    reorder_level: int
    severity: Literal["low", "critical"]
    recommended_action: str

class SalesData(TypedDict):
    total_sales: float
    total_orders: int
    period: str
    top_selling_items: List[Dict[str, Any]]
    low_stock_alerts: List[StockAlert]

class InventoryTrigger(BaseModel):
    """Represents different types of triggers that can initiate inventory monitoring"""
    
    trigger_type: Literal["low_stock", "sales_update", "manual_check", "scheduled_check"] = Field(
        description="Type of trigger that initiated the monitoring"
    )
    triggered_by: Optional[str] = Field(
        description="What or who triggered this check"
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Priority level of this trigger"
    )
    details: Dict[str, Any] = Field(
        description="Additional details about the trigger"
    ) 