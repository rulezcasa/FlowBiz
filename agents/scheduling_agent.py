from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from state.state_manager import get_state, update_state
import os
import json
from langchain.messages import SystemMessage, HumanMessage
from tools.appointment_scheduler import (
    get_service_data,
    check_availability,
    create_appointment,
)
from langsmith import traceable
from utils.helpers import timestamp_to_day_of_week
from langsmith.run_helpers import get_current_run_tree
from utils.helpers import extract_text

"""
Agent to schedule appointments

    Returns:
        str: User friendly LLM response.

Notes:
    1. Uses time only for checking stylist schedule and timestamp for appointment conflict check
    2. day_of_week mapped as (sunday to saturday : 0 to 6)

To do:
    1. Appointment checking
    2. Appointment cancelling
    3. Appointment reminders
"""


# Config
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
MODEL=os.getenv("MODEL")
model = ChatGoogleGenerativeAI(model=MODEL, google_api_key=GOOGLE_KEY)
with open("prompts/scheduling_agent.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Langchain - Create agent
agent = create_agent(
    model=model,
    tools=[get_service_data, check_availability, create_appointment],
    system_prompt=system_prompt,
)


# Call General Agent
@traceable(name="Scheduling Agent Run")
async def invoke_scheduling_agent(phone):
    current_state = None
    try:
        current_state = await get_state(phone)
        if current_state.get("entities", {}).get("appointment_date_time", {}):
            current_state["day_of_week"] = timestamp_to_day_of_week(
                current_state["entities"]["appointment_date_time"]
            )

        messages = [
            SystemMessage(
                content=f"Current orchestrator state:\n{json.dumps(current_state, indent=2)}"
            ),
            HumanMessage(content=current_state["user_message"]),  # User query
        ]

        response = await agent.ainvoke(
            {"messages": messages}
        )

        return extract_text(response)
    finally:
        if current_state:
            await update_state(
                phone,
                {
                    "active_agent": None,
                },
            )
