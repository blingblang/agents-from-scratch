import os
from typing import Literal
from pydantic import BaseModel

from langchain.chat_models import init_chat_model

from langgraph.graph import StateGraph, START, END
from langgraph.store.base import BaseStore
from langgraph.types import interrupt, Command

from src.email_assistant.tools import get_tools, get_tools_by_name
from src.email_assistant.tools.zoho.prompt_templates import DEMAND_FORECAST_TOOLS_PROMPT
from src.email_assistant.demand_forecast_prompts import (
    demand_forecast_triage_system_prompt, 
    demand_forecast_triage_user_prompt, 
    demand_forecast_agent_system_prompt_hitl_memory,
    default_demand_forecast_triage_instructions, 
    default_demand_forecast_background, 
    default_demand_forecast_response_preferences, 
    default_forecasting_analytics_preferences,
    DEMAND_FORECAST_MEMORY_UPDATE_INSTRUCTIONS
)
from src.email_assistant.demand_forecast_schemas import DemandForecastState, DemandForecastRouterSchema, DemandForecastStateInput
from src.email_assistant.demand_forecast_utils import parse_forecast_trigger, format_forecast_for_display, format_forecast_trigger_markdown
from dotenv import load_dotenv

load_dotenv(".env")

# Get tools with Zoho Demand Forecasting tools
tools = get_tools([
    "analyze_demand_patterns_tool", 
    "forecast_demand_tool", 
    "analyze_stockout_risk_tool", 
    "generate_reorder_recommendations_tool", 
    "seasonal_demand_analysis_tool", 
    "Question", 
    "Done"
], include_zoho=True)
tools_by_name = get_tools_by_name(tools)

# Initialize the LLM for use with router / structured output
llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
llm_router = llm.with_structured_output(DemandForecastRouterSchema) 

# Initialize the LLM, enforcing tool use (of any available tools) for agent
llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
llm_with_tools = llm.bind_tools(tools, tool_choice="required")

def get_memory(store, namespace, default_content=None):
    """Get memory from the store or initialize with default if it doesn't exist.
    
    Args:
        store: LangGraph BaseStore instance to search for existing memory
        namespace: Tuple defining the memory namespace, e.g. ("demand_forecast", "forecasting_preferences")
        default_content: Default content to use if memory doesn't exist
        
    Returns:
        str: The content of the memory profile, either from existing memory or the default
    """
    # Search for existing memory with namespace and key
    user_preferences = store.get(namespace, "user_preferences")
    
    # If memory exists, return its content (the value)
    if user_preferences:
        return user_preferences.value
    
    # If memory doesn't exist, add it to the store and return the default content
    else:
        # Namespace, key, value
        store.put(namespace, "user_preferences", default_content)
        user_preferences = default_content
    
    # Return the default content
    return user_preferences 

class ForecastPreferences(BaseModel):
    """Demand forecasting preferences."""
    preferences: str
    justification: str

MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT = """
Remember:
- NEVER overwrite the entire profile
- ONLY make targeted additions or changes based on explicit feedback
- PRESERVE all existing forecasting knowledge not directly contradicted
- Output the complete updated profile as a string
"""

def update_memory(store, namespace, messages):
    """Update forecasting memory profile in the store.
    
    Args:
        store: LangGraph BaseStore instance to update memory
        namespace: Tuple defining the memory namespace, e.g. ("demand_forecast", "forecasting_preferences")
        messages: List of messages to update the memory with
    """

    # Get the existing memory
    user_preferences = store.get(namespace, "user_preferences")
    # Update the memory
    llm = init_chat_model("openai:gpt-4.1", temperature=0.0).with_structured_output(ForecastPreferences)
    result = llm.invoke(
        [
            {"role": "system", "content": DEMAND_FORECAST_MEMORY_UPDATE_INSTRUCTIONS.format(current_profile=user_preferences.value, namespace=namespace)},
            {"role": "user", "content": f"Think carefully and update the forecasting memory profile based upon these user messages:"}
        ] + messages
    )
    # Save the updated memory to the store
    store.put(namespace, "user_preferences", result.preferences)

# Nodes 
def forecast_triage_router(state: DemandForecastState, store: BaseStore) -> Command[Literal["forecast_interrupt_handler", "forecast_agent", "__end__"]]:
    """Analyze forecast request to decide if we should monitor, alert, or take action.

    The triage step categorizes forecasting requests by:
    - Routine monitoring and analysis
    - Trends requiring attention 
    - Critical situations requiring immediate action
    """
    
    # Parse the forecast trigger input
    trigger_type, triggered_by, priority, details = parse_forecast_trigger(state["forecast_trigger"])
    user_prompt = demand_forecast_triage_user_prompt.format(
        trigger_type=trigger_type, triggered_by=triggered_by, details=details
    )

    # Create forecast markdown for Agent Inbox in case of notification  
    forecast_markdown = format_forecast_trigger_markdown(trigger_type, triggered_by, priority, details)

    # Search for existing forecasting preferences memory
    triage_instructions = get_memory(store, ("demand_forecast", "triage_preferences"), default_demand_forecast_triage_instructions)

    # Format system prompt with background and triage instructions
    system_prompt = demand_forecast_triage_system_prompt.format(
        background=default_demand_forecast_background,
        triage_instructions=triage_instructions,
    )

    # Run the router LLM
    result = llm_router.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    # Decision
    classification = result.classification

    # Process the classification decision
    if classification == "action_required":
        print("🚨 Classification: ACTION REQUIRED - Critical forecasting situation")
        # Next node
        goto = "forecast_agent"
        # Update the state
        update = {
            "classification_decision": result.classification,
            "priority": result.priority,
            "messages": [{"role": "user",
                            "content": f"Immediate forecasting action required: {forecast_markdown}"
                        }],
        }
        
    elif classification == "monitor":
        print("📊 Classification: MONITOR - Routine forecasting analysis")

        # Next node
        goto = "forecast_agent"
        # Update the state
        update = {
            "classification_decision": classification,
            "priority": result.priority,
            "messages": [{"role": "user",
                            "content": f"Perform routine forecasting analysis: {forecast_markdown}"
                        }],
        }

    elif classification == "alert":
        print("⚠️ Classification: ALERT - Forecasting trend requires attention") 

        # Next node
        goto = "forecast_interrupt_handler"
        # Update the state
        update = {
            "classification_decision": classification,
            "priority": result.priority,
        }

    else:
        raise ValueError(f"Invalid classification: {classification}")
    
    return Command(goto=goto, update=update)

def forecast_interrupt_handler(state: DemandForecastState, store: BaseStore) -> Command[Literal["forecast_agent", "__end__"]]:
    """Handles interrupts from the forecast triage step"""
    
    # Parse the forecast trigger input
    trigger_type, triggered_by, priority, details = parse_forecast_trigger(state["forecast_trigger"])

    # Create forecast markdown for Agent Inbox  
    forecast_markdown = format_forecast_trigger_markdown(trigger_type, triggered_by, priority, details)

    # Create messages
    messages = [{"role": "user",
                "content": f"Forecast alert to notify user about: {forecast_markdown}"
                }]

    # Create interrupt for Agent Inbox
    request = {
        "action_request": {
            "action": f"Demand Forecast Agent: {state['classification_decision']}",
            "args": {}
        },
        "config": {
            "allow_ignore": True,  
            "allow_respond": True,
            "allow_edit": False, 
            "allow_accept": False,  
        },
        # Forecast alert to show in Agent Inbox
        "description": forecast_markdown,
    }

    # Send to Agent Inbox and wait for response
    response = interrupt([request])[0]

    # If user provides feedback, go to forecast agent and use feedback  
    if response["type"] == "response":
        # Add feedback to messages 
        user_input = response["args"]
        messages.append({"role": "user",
                        "content": f"User wants to proceed with forecasting analysis. Use this feedback: {user_input}"
                        })
        # Update memory with feedback
        update_memory(store, ("demand_forecast", "triage_preferences"), [{
            "role": "user",
            "content": f"The user decided to proceed with forecasting analysis, so update the triage preferences to capture this."
        }] + messages)

        goto = "forecast_agent"

    # If user ignores alert, go to END
    elif response["type"] == "ignore":
        # Make note of the user's decision to ignore the alert
        messages.append({"role": "user",
                        "content": f"The user decided to ignore the forecast alert even though it was classified as alert. Update triage preferences to capture this."
                        })
        # Update memory with feedback 
        update_memory(store, ("demand_forecast", "triage_preferences"), messages)
        goto = END

    # Catch all other responses
    else:
        raise ValueError(f"Invalid response: {response}")

    # Update the state 
    update = {
        "messages": messages,
    }

    return Command(goto=goto, update=update)

def llm_call(state: DemandForecastState, store: BaseStore):
    """LLM decides whether to call a forecasting tool or not"""
    
    # Search for existing forecasting preferences memory
    forecast_preferences = get_memory(store, ("demand_forecast", "forecasting_preferences"), default_demand_forecast_response_preferences)
    
    # Search for existing analytics preferences memory
    analytics_preferences = get_memory(store, ("demand_forecast", "analytics_preferences"), default_forecasting_analytics_preferences)

    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    {"role": "system", "content": demand_forecast_agent_system_prompt_hitl_memory.format(
                        tools_prompt=DEMAND_FORECAST_TOOLS_PROMPT,
                        background=default_demand_forecast_background,
                        response_preferences=forecast_preferences, 
                        analytics_preferences=analytics_preferences,
                        memory_context=get_memory(store, ("demand_forecast", "learned_patterns"), "No previous forecasting patterns learned.")
                    )}
                ]
                + state["messages"]
            )
        ]
    }
    
def interrupt_handler(state: DemandForecastState, store: BaseStore) -> Command[Literal["llm_call", "__end__"]]:
    """Creates an interrupt for human review of forecasting tool calls"""
    
    # Store messages
    result = []

    # Go to the LLM call node next
    goto = "llm_call"

    # Iterate over the tool calls in the last message
    for tool_call in state["messages"][-1].tool_calls:
        
        # Allowed tools for HITL
        hitl_tools = ["generate_reorder_recommendations_tool", "forecast_demand_tool", "Question"]
        
        # If tool is not in our HITL list, execute it directly without interruption
        if tool_call["name"] not in hitl_tools:

            # Execute analysis tools without interruption
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]})
            continue
            
        # Get original forecast trigger from state
        trigger_data = state["forecast_trigger"]
        trigger_type, triggered_by, priority, details = parse_forecast_trigger(trigger_data)
        original_trigger_markdown = format_forecast_trigger_markdown(trigger_type, triggered_by, priority, details)
        
        # Format tool call for display and prepend the original trigger
        tool_display = format_forecast_for_display(tool_call["args"])
        description = original_trigger_markdown + f"\n\n## Recommended Action\n\n**Tool:** {tool_call['name']}\n\n**Parameters:**\n{tool_display}"

        # Configure what actions are allowed in Agent Inbox
        if tool_call["name"] == "generate_reorder_recommendations_tool":
            config = {
                "allow_ignore": True,
                "allow_respond": True,
                "allow_edit": True,
                "allow_accept": True,
            }
        elif tool_call["name"] == "forecast_demand_tool":
            config = {
                "allow_ignore": True,
                "allow_respond": True,
                "allow_edit": True,
                "allow_accept": True,
            }
        elif tool_call["name"] == "Question":
            config = {
                "allow_ignore": True,
                "allow_respond": True,
                "allow_edit": False,
                "allow_accept": False,
            }
        else:
            raise ValueError(f"Invalid tool call: {tool_call['name']}")

        # Create the interrupt request
        request = {
            "action_request": {
                "action": tool_call["name"],
                "args": tool_call["args"]
            },
            "config": config,
            "description": description,
        }

        # Send to Agent Inbox and wait for response
        response = interrupt([request])[0]

        # Handle the responses 
        if response["type"] == "accept":

            # Execute the tool with original args
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]})
                        
        elif response["type"] == "edit":

            # Tool selection 
            tool = tools_by_name[tool_call["name"]]
            initial_tool_call = tool_call["args"]
            
            # Get edited args from Agent Inbox
            edited_args = response["args"]["args"]

            # Update the AI message's tool call with edited content (reference to the message in the state)
            ai_message = state["messages"][-1] # Get the most recent message from the state
            current_id = tool_call["id"] # Store the ID of the tool call being edited
            
            # Create a new list of tool calls by filtering out the one being edited and adding the updated version
            updated_tool_calls = [tc for tc in ai_message.tool_calls if tc["id"] != current_id] + [
                {"type": "tool_call", "name": tool_call["name"], "args": edited_args, "id": current_id}
            ]

            # Create a new copy of the message with updated tool calls
            result.append(ai_message.model_copy(update={"tool_calls": updated_tool_calls}))

            # Save feedback in memory and execute the tool with edited content
            if tool_call["name"] == "generate_reorder_recommendations_tool":
                
                # Execute the tool with edited args
                observation = tool.invoke(edited_args)
                
                # Add only the tool response message
                result.append({"role": "tool", "content": observation, "tool_call_id": current_id})

                # Update the memory with forecasting preferences
                update_memory(store, ("demand_forecast", "forecasting_preferences"), [{
                    "role": "user",
                    "content": f"User edited the reorder recommendations. Initial: {initial_tool_call}. Edited: {edited_args}. {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}"
                }])
            
            elif tool_call["name"] == "forecast_demand_tool":
                
                # Execute the tool with edited args
                observation = tool.invoke(edited_args)
                
                # Add only the tool response message
                result.append({"role": "tool", "content": observation, "tool_call_id": current_id})

                # Update the memory with forecasting method preferences
                update_memory(store, ("demand_forecast", "forecasting_preferences"), [{
                    "role": "user",
                    "content": f"User edited the demand forecast parameters. Initial: {initial_tool_call}. Edited: {edited_args}. {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}"
                }])
            
            # Catch all other tool calls
            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")

        elif response["type"] == "ignore":

            if tool_call["name"] == "generate_reorder_recommendations_tool":
                # Don't execute the tool, and tell the agent how to proceed
                result.append({"role": "tool", "content": "User ignored the reorder recommendations. Continue with analysis but do not suggest ordering.", "tool_call_id": tool_call["id"]})
                # Update memory
                update_memory(store, ("demand_forecast", "triage_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"The user ignored reorder recommendations. Update preferences to be more conservative about ordering suggestions. {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}"
                }])

            elif tool_call["name"] == "forecast_demand_tool":
                # Don't execute the tool, and tell the agent how to proceed
                result.append({"role": "tool", "content": "User ignored the demand forecast. Continue with different analysis approach.", "tool_call_id": tool_call["id"]})
                # Update memory
                update_memory(store, ("demand_forecast", "triage_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"The user ignored the demand forecast. Update preferences about when to perform detailed forecasting. {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}"
                }])

            elif tool_call["name"] == "Question":
                # Don't execute the tool, and tell the agent how to proceed
                result.append({"role": "tool", "content": "User ignored the question. Proceed with best assumptions and complete the analysis.", "tool_call_id": tool_call["id"]})
                # Update memory
                update_memory(store, ("demand_forecast", "triage_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"The user ignored the clarifying question. Update preferences to reduce questioning and be more autonomous. {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}"
                }])

            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")

        elif response["type"] == "response":
            # User provided feedback
            user_feedback = response["args"]
            if tool_call["name"] == "generate_reorder_recommendations_tool":
                # Don't execute the tool, and add a message with the user feedback
                result.append({"role": "tool", "content": f"User provided feedback on reorder recommendations: {user_feedback}", "tool_call_id": tool_call["id"]})
                # Update memory
                update_memory(store, ("demand_forecast", "forecasting_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"User provided feedback on reorder recommendations. Use this to update forecasting preferences. {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}"
                }])

            elif tool_call["name"] == "forecast_demand_tool":
                # Don't execute the tool, and add a message with the user feedback
                result.append({"role": "tool", "content": f"User provided feedback on demand forecasting: {user_feedback}", "tool_call_id": tool_call["id"]})
                # Update memory
                update_memory(store, ("demand_forecast", "forecasting_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"User provided feedback on demand forecasting methods. Use this to update forecasting preferences. {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}"
                }])

            elif tool_call["name"] == "Question":
                # Don't execute the tool, and add a message with the user feedback
                result.append({"role": "tool", "content": f"User answered the question: {user_feedback}", "tool_call_id": tool_call["id"]})

            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")

    # Update the state 
    update = {
        "messages": result,
    }

    return Command(goto=goto, update=update)

# Conditional edge function
def should_continue(state: DemandForecastState, store: BaseStore) -> Literal["interrupt_handler", "__end__"]:
    """Route to tool handler, or end if Done tool called"""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls: 
            if tool_call["name"] == "Done":
                return END
            else:
                return "interrupt_handler"

# Build workflow
agent_builder = StateGraph(DemandForecastState)

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
agent_builder.add_edge("interrupt_handler", "llm_call")

# Compile the agent
forecast_agent = agent_builder.compile()

# Build overall workflow with store and checkpointer
overall_workflow = (
    StateGraph(DemandForecastState, input=DemandForecastStateInput)
    .add_node(forecast_triage_router)
    .add_node(forecast_interrupt_handler)
    .add_node("forecast_agent", forecast_agent)
    .add_edge(START, "forecast_triage_router")
    .add_conditional_edges(
        "forecast_triage_router",
        lambda state: state["classification_decision"],
        {
            "action_required": "forecast_agent",
            "monitor": "forecast_agent", 
            "alert": "forecast_interrupt_handler",
        },
    )
    .add_conditional_edges(
        "forecast_interrupt_handler",
        lambda state: "forecast_agent" if state.get("messages") else END,
        {
            "forecast_agent": "forecast_agent",
            END: END
        }
    )
    .add_edge("forecast_agent", END)
)

demand_forecast_agent = overall_workflow.compile() 