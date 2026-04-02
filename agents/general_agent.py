from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from state.state_manager import get_state
import os

"""
    Agent to answer general questions about the saloon

    Returns:
        str: User friendly LLM response.
"""

# --- Config --- 
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY") 

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_KEY)

with open("prompts/general_agent.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

agent=create_agent(
        model=model, 
        system_prompt = system_prompt
        )


def invoke_general_agent(phone):
    current_state=get_state(phone)
    response = agent.invoke({
        'messages': [
            {'role': 'user', 'content' : current_state['user_message']}
        ]
    }   )

    return response["messages"][-1].content

    





