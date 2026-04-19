from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from state.state_manager import get_state, update_state
import os
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree
from langchain.messages import SystemMessage, HumanMessage
import json
from utils.helpers import extract_text

"""
    Agent to answer general questions about the saloon

    Returns:
        str: User friendly LLM response.
"""

# Config
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
MODEL=os.getenv("MODEL")
model = ChatGoogleGenerativeAI(model=MODEL, google_api_key=GOOGLE_KEY)
with open("prompts/general_agent.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Langchain - Create agent
agent = create_agent(model=model, system_prompt=system_prompt)


# Call General Agent
@traceable(name="General Agent Run")
async def invoke_general_agent(phone):
    current_state = None
    try:
        current_state = await get_state(phone)

        run_tree = get_current_run_tree()
        if run_tree:
            run_tree.metadata.update({
            "phone": phone,
            "user_id": current_state.get("user_id"),
        })
            
        messages = [
        SystemMessage(
            content = f"Customer name: {current_state.get('entities', {}).get('name', 'Unknown')}"
        ),
        HumanMessage(content=current_state["user_message"]),
        ]

        response = await agent.ainvoke(
            {"messages": messages},
        )

        return extract_text(response)
    finally:
        if current_state:
            await update_state(phone, {"active_agent": None})
