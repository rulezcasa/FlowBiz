from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from state.state_manager import get_state, update_state
import os
from datetime import datetime
import json
from langchain.messages import SystemMessage, HumanMessage
from tools.appointment_scheduler import get_service_data, check_availability, create_appointment

'''
Agent to schedule appointments

    Returns:
        str: User friendly LLM response.

Notes:
    1. Uses time only for checking stylist schedule and timestamp for appointment conflict check
    2. day_of_week mapped as (sunday to saturday : 0 to 1)
'''


#Config
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY") 
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_KEY)
with open("prompts/scheduling_agent.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Langchain - Create agent 
agent=create_agent(
        model=model, 
        tools=[get_service_data, check_availability, create_appointment],
        system_prompt = system_prompt,
        )

# Call General Agent
def invoke_scheduling_agent(phone):
    current_state = None
    try:
        current_state=get_state(phone)
        # current_state['day_of_week'] = timestamp_to_day_of_week(current_state['entities']['appointment_date_time'])
        current_state['day_of_week'] = 0
        current_state['entities']['appointment_date_time']='2025-04-05T15:00:00'

        messages = [
        SystemMessage(content=f"Current orchestrator state:\n{json.dumps(current_state, indent=2)}"),
        HumanMessage(content=current_state['user_message'])  # User query
    ]

        response = agent.invoke({
            'messages': messages
        }       )

        print(response["messages"][-1].content)
    finally:
        if current_state:
            update_state(phone, {
                "active_agent": None,
                "flow_locked" : False
            })


# Utility Function - Convert timestamp to day of the week
def timestamp_to_day_of_week(timestamp: str) -> int:
    dt = datetime.fromisoformat(timestamp)
    return (dt.weekday() + 1) % 7
