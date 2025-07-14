from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict, Literal, Annotated
from langgraph.graph import MessagesState

class RestockRouterSchema(BaseModel):
    """Analyze restock requests and route them according to their urgency and type."""

    reasoning: str = Field(
        description="Step-by-step reasoning behind the classification."
    )
    classification: Literal["monitor", "alert", "action_required"] = Field(
        description="The classification of restock situation: 'monitor' for routine procurement, "
        "'alert' for situations needing attention but not urgent, "
        "'action_required' for critical restocking situations requiring immediate action",
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Priority level of the restock request"
    )

class RestockStateInput(TypedDict):
    # This is the input to the state for restock management
    restock_trigger: Dict[str, Any]  # Could be stockout alert, reorder request, etc.

class RestockState(MessagesState):
    # This state class has the messages key built in from MessagesState
    restock_trigger: Dict[str, Any]
    classification_decision: Literal["monitor", "alert", "action_required"]
    priority: Literal["low", "medium", "high", "critical"]

class SupplierInfo(TypedDict):
    supplier_id: str
    name: str
    contact_person: str
    email: str
    phone: str
    category: str
    lead_time_days: int
    minimum_order: float
    payment_terms: str
    rating: float
    products: List[str]
    pricing: Dict[str, Dict[str, float]]  # item_name -> {unit_cost, bulk_discount}

class SupplierQuote(TypedDict):
    supplier_id: str
    supplier_name: str
    item_name: str
    quantity: int
    unit_cost: float
    final_price: float
    total_cost: float
    lead_time_days: int
    minimum_order: float
    meets_minimum: bool
    bulk_discount_applied: bool
    payment_terms: str
    rating: float

class PurchaseOrder(TypedDict):
    po_number: str
    supplier_id: str
    supplier_name: str
    supplier_contact: str
    item_name: str
    quantity: int
    unit_cost: float
    final_price: float
    total_cost: float
    order_date: str
    requested_delivery: str
    expected_delivery: str
    lead_time_days: int
    payment_terms: str
    status: Literal["Pending Approval", "Approved - Sent to Supplier", "Confirmed by Supplier", "In Transit", "Delivered", "Cancelled"]
    notes: str
    bulk_discount_applied: bool
    approval_date: Optional[str]
    approval_notes: Optional[str]
    cancellation_date: Optional[str]
    cancellation_reason: Optional[str]

class RestockRequest(TypedDict):
    item_name: str
    current_stock: int
    reorder_level: int
    requested_quantity: int
    urgency: Literal["low", "medium", "high", "critical"]
    reason: str
    budget_limit: Optional[float]
    preferred_suppliers: Optional[List[str]]
    delivery_deadline: Optional[str]

class BulkRestockItem(TypedDict):
    item_name: str
    quantity: int
    priority: Literal["low", "medium", "high", "critical"]
    current_stock: int
    target_stock: int

class BulkRestockPlan(TypedDict):
    items: List[BulkRestockItem]
    total_budget: Optional[float]
    delivery_deadline: Optional[str]
    supplier_preferences: Optional[List[str]]
    cost_optimization: bool

class SupplierPerformance(TypedDict):
    supplier_id: str
    supplier_name: str
    total_orders: int
    total_value: float
    average_order_value: float
    on_time_delivery_rate: float
    quality_rating: float
    price_competitiveness: float
    communication_score: float
    overall_rating: float
    last_order_date: Optional[str]
    preferred_categories: List[str]

class RestockTrigger(BaseModel):
    """Represents different types of triggers that can initiate restocking"""
    
    trigger_type: Literal["stockout_alert", "reorder_request", "seasonal_prep", "supplier_promotion", "budget_cycle", "emergency_order"] = Field(
        description="Type of trigger that initiated the restocking"
    )
    triggered_by: Optional[str] = Field(
        description="What or who triggered this restock request"
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Priority level of this restock request"
    )
    details: Dict[str, Any] = Field(
        description="Additional details about the restock trigger"
    )
    items_affected: Optional[List[str]] = Field(
        description="Specific items that need restocking (if any)"
    )
    budget_limit: Optional[float] = Field(
        description="Budget limit for this restocking activity"
    )
    delivery_deadline: Optional[str] = Field(
        description="Required delivery deadline (YYYY-MM-DD)"
    )

class OrderApproval(TypedDict):
    po_number: str
    approved_by: str
    approval_date: str
    approval_amount: float
    approval_notes: str
    conditions: Optional[List[str]]

class SupplierSelection(TypedDict):
    item_name: str
    quantity: int
    recommended_supplier: SupplierQuote
    alternative_suppliers: List[SupplierQuote]
    selection_criteria: str
    cost_savings: float
    risk_assessment: str

class OrderTracking(TypedDict):
    po_number: str
    current_status: str
    status_date: str
    expected_delivery: str
    actual_delivery: Optional[str]
    tracking_number: Optional[str]
    delivery_issues: Optional[List[str]]
    supplier_updates: Optional[List[str]]

class ProcurementMetrics(TypedDict):
    total_orders: int
    total_value: float
    average_order_value: float
    cost_savings: float
    on_time_delivery_rate: float
    supplier_performance_avg: float
    budget_utilization: float
    emergency_orders: int

class InventoryImpact(TypedDict):
    item_name: str
    current_stock: int
    incoming_stock: int
    projected_stock: int
    days_of_supply: int
    stockout_risk: Literal["low", "medium", "high", "critical"]
    reorder_recommendation: str

class CostAnalysis(TypedDict):
    item_name: str
    quantity: int
    base_cost: float
    bulk_discount: float
    total_cost: float
    cost_per_unit: float
    savings_percentage: float
    comparison_suppliers: List[Dict[str, Any]]

class DeliverySchedule(TypedDict):
    po_number: str
    supplier_name: str
    items: List[str]
    order_date: str
    expected_delivery: str
    lead_time_days: int
    delivery_priority: Literal["standard", "expedited", "emergency"]
    special_instructions: Optional[str]

class BudgetTracking(TypedDict):
    period: str  # monthly, quarterly, yearly
    total_budget: float
    spent_to_date: float
    remaining_budget: float
    committed_orders: float
    available_budget: float
    budget_utilization_percent: float
    projected_spending: float

class SupplierCommunication(TypedDict):
    supplier_id: str
    communication_type: Literal["order_request", "status_inquiry", "issue_report", "performance_review"]
    message: str
    sent_date: str
    response_required: bool
    response_deadline: Optional[str]
    priority: Literal["low", "medium", "high", "urgent"] 