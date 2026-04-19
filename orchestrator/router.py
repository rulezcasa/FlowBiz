import os
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from state.state_manager import get_state, update_state
from agents.service_agent import invoke_service_agent
from agents.general_agent import invoke_general_agent
from agents.scheduling_agent import invoke_scheduling_agent
import json
from collections import deque
from langsmith.run_helpers import get_current_run_tree
from utils.helpers import extract_text

"""
    Orchestrator model to extract intent, build state and dispatch queries to agents
"""

# Config
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
MODEL=os.getenv("MODEL")
model = init_chat_model(
    model=MODEL,
    model_provider="google_genai",  # critical
    google_api_key=GOOGLE_KEY
)
with open("prompts/router.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()


# Dispatcher : based on the active agent set by the orchestrator, invoke the corresponding agent
async def dispatcher(phone, agent):
    # Service Agent
    if agent=='service_agent':
        response=await invoke_service_agent(phone)
        return response

    # General Agent
    if agent=='general_agent':
        response=await invoke_general_agent(phone)
        return response
    
    # Scheduling Agent
    if agent=='scheduling_agent':
        response=await invoke_scheduling_agent(phone)
        return response
    

# Orchestrator : Entry point into the agentic layer - extracts intent/entities and calls dispatcher.
async def orchestrate(phone,message=None):
    saved_state=await get_state(phone)
    history = saved_state.get("conversation_history", []) # Retrieve conversation history if available
    history = deque(history, maxlen=5) # Conversation history of size 5 (deque)

    messages = [
        SystemMessage(content=system_prompt),
        SystemMessage(content=f"Current orchestrator state:\n{json.dumps(saved_state, indent=2)}"),
        HumanMessage(content=message)    # User query
    ]

    response=await model.ainvoke(messages)

    content = response.content

    if isinstance(content, list):
        content = " ".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )   

    llm_state = json.loads(
        content.replace("```json", "").replace("```", "").strip()
    )

    updated_state = {
        "user_id": saved_state['user_id'],
        "phone" : saved_state['phone'],
        "active_agent": llm_state["active_agent"],
        "active_flow": llm_state["active_flow"],
        "entities": llm_state["entities"],
        "user_message": llm_state["user_message"],
    }

    await update_state(phone,updated_state)

    response= await dispatcher(phone,updated_state["active_agent"])

    history.append({"role": "user", "content": llm_state["user_message"]})
    history.append({"role": "assistant", "content": response})

    updated_state["conversation_history"] = list(history)
    await update_state(phone, updated_state)

    return response




