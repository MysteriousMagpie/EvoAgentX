"""
Example integration of the intent classifier into the Obsidian chat endpoint.

This file demonstrates how to modify the existing /api/obsidian/chat endpoint
to automatically classify intent and set the mode accordingly.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, List, Optional

# This would be added to the existing obsidian.py imports
from evoagentx.intents import classify_intent, explain_intent, Intent

# Example of how the chat endpoint could be modified to use automatic classification


async def enhanced_chat_with_agent(request: AgentChatRequest):
    """
    Enhanced chat endpoint with automatic intent classification.
    
    This is an example of how the existing chat endpoint could be modified
    to automatically determine the mode using the intent classifier.
    """
    try:
        conversation_id = get_or_create_conversation(request.conversation_id)
        
        # Add user message to conversation
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now()
        )
        conversations[conversation_id].append(user_message)
        
        # AUTO-CLASSIFY INTENT IF MODE NOT EXPLICITLY SET
        if request.mode is None or hasattr(request, 'auto_classify') and request.auto_classify:
            try:
                # Use intent classifier to determine mode
                intent_result = await classify_intent(request.message)
                
                # Set mode based on classification
                if intent_result.intent == Intent.AGENT:
                    determined_mode = "agent"
                else:
                    determined_mode = "ask"
                
                print(f"[INTENT] Auto-classified '{request.message}' as {determined_mode} "
                      f"(confidence: {intent_result.confidence:.3f})")
                
                # Use the classified mode
                effective_mode = determined_mode
                
            except Exception as e:
                print(f"[INTENT ERROR] Failed to classify intent: {e}")
                # Fallback to default mode
                effective_mode = request.mode or "ask"
        else:
            # Use explicitly provided mode
            effective_mode = request.mode or "ask"
        
        # Handle different modes (existing logic)
        if effective_mode == "agent":
            # Agent mode: Execute workflow for complex tasks
            try:
                from evoagentx.core.runner import run_workflow_async
                result, graph = await run_workflow_async(
                    goal=request.message,
                    return_graph=True
                )
                response_text = str(result)
                agent_name = "WorkflowAgent"
            except Exception as e:
                print(f"[WORKFLOW ERROR] Exception during workflow execution: {str(e)}")
                response_text = f"Workflow execution error: {str(e)}"
                agent_name = "WorkflowAgent"
        else:
            # Ask mode: Simple chat with agent
            try:
                # Get or create agent
                if request.agent_name and request.agent_name in active_agents:
                    agent = active_agents[request.agent_name]
                else:
                    agent = get_default_agent()
                
                agent_name = agent.name
                
                # Use the agent's default action
                if hasattr(agent, 'actions') and agent.actions:
                    action_name = agent.actions[0].name
                    result = await agent.async_execute(
                        action_name=action_name,
                        action_input_data={"query": request.message}
                    )
                    response_text = str(result)
                else:
                    response_text = "Agent has no available actions"
                    
            except Exception as e:
                print(f"[AGENT ERROR] Exception during agent execution: {str(e)}")
                response_text = f"Agent execution error: {str(e)}"
                agent_name = "DefaultAgent"
        
        # Add assistant response to conversation
        assistant_message = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.now()
        )
        conversations[conversation_id].append(assistant_message)
        
        # Prepare metadata with mode info
        metadata = {
            "effective_mode": effective_mode,
            "original_mode": request.mode,
        }
        
        # If auto-classification was used, include debug info
        if request.mode is None or (hasattr(request, 'auto_classify') and request.auto_classify):
            try:
                debug_result = await explain_intent(request.message)
                metadata.update({
                    "intent_classification": {
                        "classified_intent": debug_result.intent.value,
                        "confidence": debug_result.confidence,
                        "top_example": debug_result.top_example,
                        "example_score": debug_result.example_score
                    }
                })
            except Exception:
                pass  # Don't fail the whole request if debug info fails
        
        return AgentChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            agent_name=agent_name,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
    except Exception as e:
        print(f"[CHAT ERROR] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# Alternative: Add a dedicated endpoint for intent classification
async def classify_message_intent(message: str):
    """
    Dedicated endpoint for testing intent classification.
    
    This could be useful for debugging and development.
    """
    try:
        result = await explain_intent(message)
        return {
            "message": message,
            "intent": result.intent.value,
            "confidence": result.confidence,
            "top_example": result.top_example,
            "example_score": result.example_score,
            "recommended_mode": result.intent.value  # "ask" or "agent"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


# Example usage in router
"""
# Add to existing obsidian.py router:

@router.post("/classify-intent")
async def classify_intent_endpoint(request: Dict[str, str]):
    '''Classify the intent of a message'''
    message = request.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    return await classify_message_intent(message)

# Or modify the existing chat endpoint to include auto-classification
@router.post("/chat", response_model=AgentChatResponse)  
async def chat_with_agent(request: AgentChatRequest):
    '''Chat with an agent in a conversational manner or execute workflows based on mode'''
    return await enhanced_chat_with_agent(request)
"""
