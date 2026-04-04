from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.query_catalogue import get_services
from dotenv import load_dotenv
from state.state_manager import get_state, update_state
import os

"""
    Agent to Fetch salon services filtered by category and gender and respond to user query.

    Returns:
        str: User friendly LLM response with appointment confirmation

    Notes:
        To do : 
            1. Add status column to appointment_data table
            2. Appointment cancelling and rescheduling
"""

# Config 
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY") 
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_KEY)
with open("prompts/service_agent.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Langchain - Create agent 
agent=create_agent(
        model=model, 
        tools=[get_services],
        system_prompt = system_prompt
        )

# Call Service Agent
def invoke_service_agent(phone):
    current_state = None
    try:
        current_state = get_state(phone)
        response = agent.invoke({
            'messages': [
                {'role': 'user', 'content': current_state['user_message']}
            ]
        })
        return response["messages"][-1].content

    finally:
        if current_state:
            update_state(phone, {
                "active_agent": None
            })


    





