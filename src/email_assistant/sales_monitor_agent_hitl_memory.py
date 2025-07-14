import os
from typing import Literal
from pydantic import BaseModel

from langchain.chat_models import init_chat_model

from langgraph.graph import StateGraph, START, END
from langgraph.store.base import BaseStore
from langgraph.types import interrupt, Command

from src.email_assistant.tools import get_tools, get_tools_by_name
from src.email_assistant.tools.zoho.prompt_templates import ZOHO_TOOLS_PROMPT
from src.email_assistant.inventory_prompts import (
    inventory_triage_system_prompt, 
    inventory_triage_user_prompt, 
    sales_monitor_agent_system_prompt_hitl_memory,
    default_inventory_triage_instructions, 
    default_inventory_background, 
    default_inventory_response_preferences, 
    default_analytics_preferences
)
from src.email_assistant.inventory_schemas import InventoryState, InventoryRouterSchema, InventoryStateInput
from src.email_assistant.inventory_utils import parse_inventory_trigger, format_for_display, format_inventory_trigger_markdown
from dotenv import load_dotenv

load_dotenv(".env")

# Get tools with Zoho Inventory tools
tools = get_tools(["fetch_inventory_tool", "check_stock_levels_tool", "get_sales_analytics_tool", "create_order_tool", "update_inventory_tool", "Question", "Done"], include_zoho=True)
tools_by_name = get_tools_by_name(tools)

# Initialize the LLM for use with router / structured output
llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
llm_router = llm.with_structured_output(InventoryRouterSchema) 

# Initialize the LLM, enforcing tool use (of any available tools) for agent
llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
llm_with_tools = llm.bind_tools(tools, tool_choice="required")

def get_memory(store, namespace, default_content=None):
    """Get memory from the store or initialize with default if it doesn't exist.
    
    Args:
        store: LangGraph BaseStore instance to search for existing memory
        namespace: Tuple defining the memory namespace, e.g. ("sales_monitor", "inventory_preferences")
        default_content: Default content to use if memory doesn't exist
        
    Returns:
        str: The content of the memory profile, either from existing memory or the default
    """
    # Search for existing memory with namespace and key
    user_preferences = store.get(namespace, "user_preferences")
    
    # If memory exists, return its content (the value)
    if user_preferences:
        return user_preferences.value
    
    # If no memory exists, return default content or empty string
    return default_content or ""

def update_memory(store, namespace, content):
    """Update memory in the store.
    
    Args:
        store: LangGraph BaseStore instance to store memory
        namespace: Tuple defining the memory namespace
        content: Content to store in memory
    """
    store.put(namespace, "user_preferences", content)

# Nodes
def llm_call(state: InventoryState):
    """LLM decides which tool to call for inventory monitoring"""
    
    # Get memory context for this user
    memory_context = get_memory(
        state["store"], 
        ("sales_monitor", "inventory_preferences"),
        "No previous preferences recorded. This is a new interaction."
    )

    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    {"role": "system", "content": sales_monitor_agent_system_prompt_hitl_memory.format(
                        tools_prompt=ZOHO_TOOLS_PROMPT,
                        memory_context=memory_context,
                        background=default_inventory_background,
                        response_preferences=default_inventory_response_preferences, 
                        analytics_preferences=default_analytics_preferences)
                    },
                    
                ]
                + state["messages"]
            )
        ]
    }

def should_continue(state: InventoryState) -> Literal["interrupt_handler", END]:
    """Route to interrupt handler, or end if Done tool called"""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls: 
            if tool_call["name"] == "Done":
                return END
            else:
                return "interrupt_handler"

def interrupt_handler(state: InventoryState):
    """Handle tool calls with human-in-the-loop for critical decisions"""
    
    messages = state["messages"]
    last_message = messages[-1]
    
    # Process each tool call
    tool_responses = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        
        # Check if this is a Question tool - if so, interrupt for human input
        if tool_name == "Question":
            # Format the question for display
            question_content = tool_call["args"].get("content", "No question provided")
            
            # Create interrupt data for Agent Inbox
            interrupt_data = {
                "type": "question",
                "question": question_content,
                "timestamp": "2025-01-14T12:00:00Z",
                "context": "Inventory monitoring requires human input"
            }
            
            # Interrupt and wait for human response
            human_response = interrupt(interrupt_data)
            
            # Process the human response
            response_content = f"Human Response: {human_response}"
            
        # Check if this is a critical action requiring approval
        elif tool_name in ["create_order_tool", "update_inventory_tool"]:
            tool_args = tool_call["args"]
            
            # Determine if approval is needed based on business rules
            needs_approval = False
            approval_reason = ""
            
            if tool_name == "create_order_tool":
                # Check if order value exceeds threshold
                # Note: We'd need to calculate order value, for now assume approval needed for orders
                needs_approval = True
                approval_reason = "Order creation requires approval"
                
            elif tool_name == "update_inventory_tool":
                # Check if quantity change is significant
                new_quantity = tool_args.get("new_quantity", 0)
                if new_quantity > 25:  # Threshold for approval
                    needs_approval = True
                    approval_reason = f"Large inventory update ({new_quantity} units) requires approval"
            
            if needs_approval:
                # Create approval request
                approval_data = {
                    "type": "approval",
                    "action": tool_name,
                    "args": tool_args,
                    "reason": approval_reason,
                    "timestamp": "2025-01-14T12:00:00Z"
                }
                
                # Interrupt for approval
                approval_response = interrupt(approval_data)
                
                if approval_response and approval_response.lower() in ["yes", "approve", "approved"]:
                    # Execute the tool if approved
                    tool = tools_by_name[tool_name]
                    response_content = tool.invoke(tool_args)
                else:
                    response_content = f"Action {tool_name} was not approved by user."
            else:
                # Execute tool without approval
                tool = tools_by_name[tool_name]
                response_content = tool.invoke(tool_args)
        else:
            # Execute other tools normally
            tool = tools_by_name[tool_name]
            tool_args = tool_call["args"]
            response_content = tool.invoke(tool_args)
        
        # Create tool response message
        tool_responses.append({
            "role": "tool",
            "content": response_content,
            "tool_call_id": tool_call["id"]
        })
    
    return {"messages": tool_responses}

def inventory_triage_router(state: InventoryState) -> Command[Literal["response_agent", END]]:
    """Analyze inventory trigger to decide if we should monitor, alert, or take action.

    The triage step determines the urgency and routes accordingly:
    - MONITOR: Routine checks, normal operations
    - ALERT: Items needing attention but not urgent
    - ACTION_REQUIRED: Critical situations requiring immediate response
    """
    trigger_type, triggered_by, priority, details = parse_inventory_trigger(state["inventory_trigger"])
    
    system_prompt = inventory_triage_system_prompt.format(
        background=default_inventory_background,
        triage_instructions=default_inventory_triage_instructions
    )

    user_prompt = inventory_triage_user_prompt.format(
        trigger_type=trigger_type, 
        triggered_by=triggered_by, 
        details=details
    )

    # Create trigger markdown for Agent Inbox in case of notification  
    trigger_markdown = format_inventory_trigger_markdown(trigger_type, triggered_by, priority, details)

    # Run the router LLM
    result = llm_router.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    # Decision logic
    classification = result.classification
    
    if classification == "action_required":
        return Command(
            goto="response_agent",
            update={
                "classification_decision": classification,
                "priority": result.priority,
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Inventory situation requires action:\n\n{trigger_markdown}\n\nReasoning: {result.reasoning}"
                    }
                ],
            },
        )
    elif classification == "alert":
        return Command(
            goto="response_agent",
            update={
                "classification_decision": classification,
                "priority": result.priority,
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Inventory alert:\n\n{trigger_markdown}\n\nReasoning: {result.reasoning}"
                    }
                ],
            },
        )
    else:  # monitor
        return Command(
            goto="response_agent",
            update={
                "classification_decision": classification,
                "priority": result.priority,
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Routine inventory monitoring:\n\n{trigger_markdown}\n\nReasoning: {result.reasoning}"
                    }
                ],
            },
        )

def triage_interrupt_handler(state: InventoryState):
    """Handle interrupts for triage decisions that may need human oversight"""
    
    # For high priority situations, we might want to notify humans
    if state.get("priority") in ["high", "critical"]:
        # Create notification data
        notification_data = {
            "type": "notification",
            "classification": state.get("classification_decision"),
            "priority": state.get("priority"),
            "trigger": state["inventory_trigger"],
            "timestamp": "2025-01-14T12:00:00Z"
        }
        
        # This could send a notification to Agent Inbox or other systems
        # For now, we'll just continue without interrupting
        pass
    
    return {}

# Build workflow
agent_builder = StateGraph(InventoryState)

# Add nodes - with store parameter
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("interrupt_handler", interrupt_handler)

# Add edges
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "interrupt_handler": "interrupt_handler",
        END: END,
    },
)

# Compile the agent
response_agent = agent_builder.compile()

# Build overall workflow with store and checkpointer
overall_workflow = (
    StateGraph(InventoryState, input=InventoryStateInput)
    .add_node(inventory_triage_router)
    .add_node(triage_interrupt_handler)
    .add_node("response_agent", response_agent)
    .add_edge(START, "inventory_triage_router")
)

sales_monitor_agent = overall_workflow.compile() 