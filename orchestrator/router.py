import os
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from state.state_manager import get_state, update_state
from agents.service_agent import invoke_service_agent
from agents.general_agent import invoke_general_agent
import json

load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")

model = init_chat_model("gemini-2.5-flash")

with open("prompts/router.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

def dispatcher(user_id, phone, agent):
    
    if agent=='service_agent':
        response=invoke_service_agent(phone)
        print(response)

        update_state(user_id,
            {
            "active_agent" : None
            }
        )
    
    if agent=='general_agent':
        response=invoke_general_agent(phone)
        print(response)

        update_state(user_id,
            {
            "active_agent" : None
            }
        )
    

def router_model(phone):
    saved_state=get_state(phone)

    messages = [
        SystemMessage(content=system_prompt),  # System prompt goes first
        SystemMessage(content=f"Current orchestrator state:\n{json.dumps(saved_state, indent=2)}"),
        HumanMessage(content="When will the war end?")  # User query
    ]

    response=model.invoke(messages)

    llm_state = json.loads(response.content.replace("```json", "").replace("```", "").strip())

    updated_state = {
        "user_id": saved_state['user_id'],
        "phone" : saved_state['phone'],
        "active_agent": llm_state["active_agent"],
        "active_flow": llm_state["active_flow"],
        "flow_locked": llm_state["flow_locked"],
        "entities": llm_state["entities"],
        "user_message": llm_state["user_message"]
    }

    update_state(saved_state["user_id"],updated_state)

    dispatcher(saved_state["user_id"],phone,updated_state["active_agent"])


router_model('9035790945')


