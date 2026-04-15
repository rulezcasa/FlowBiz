from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.query_catalogue import get_services
from dotenv import load_dotenv
from langchain.messages import SystemMessage, HumanMessage
from state.state_manager import get_state, update_state
import os
from langsmith import traceable
import json
from utils.helpers import extract_text
from langsmith.run_helpers import get_current_run_tree

"""
    Agent to Fetch salon services filtered by category and gender and respond to user query.

    Returns:
        str: User friendly LLM response with appointment confirmation

    Notes:
        To do : 
            1. Appointment cancelling and rescheduling
"""

# Config
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_KEY)
with open("prompts/service_agent.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Langchain - Create agent
agent = create_agent(model=model, tools=[get_services], system_prompt=system_prompt)


# Call Service Agent
@traceable(name="Service Agent Run")
def invoke_service_agent(phone):
    current_state = None
    try:
        current_state = get_state(phone)

        run_tree = get_current_run_tree()
        if run_tree:
            run_tree.metadata.update({
            "phone": phone,
            "user_id": current_state.get("user_id"),
        })


        messages = [
            SystemMessage(
                content=f"Current orchestrator state:\n{json.dumps(current_state, indent=2)}"
            ),
            HumanMessage(content=current_state["user_message"]),  # User query
        ]

        response = agent.invoke(
            {"messages": messages},
        )
        return extract_text(response)

    finally:
        if current_state:
            update_state(phone, {"active_agent": None})
