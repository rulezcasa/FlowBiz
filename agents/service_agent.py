from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.query_catalogue import get_services
from dotenv import load_dotenv
import os

"""
    Agent to Fetch salon services filtered by category and gender and respond to user query.

    Returns:
        str: User friendly LLM response.

    Notes:
        To do : Multiple category queries.
        Try out prompt markup language (.pml)
"""

# --- Config ---
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY") 

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", gemini_api_key=GEMINI_KEY)

agent=create_agent(
    model=model, 
    tools=[get_services],
system_prompt = """
You are a Service Catalogue Assistant for a salon.

Male Categories:
["face_bleach", 
"face_cleanup", 
"head_massage", 
"advanced_facial", 
"dtan", 
"haircolor", 
"basic_facial", 
"hairspa", 
"face_make_up", 
"hair_and_styling"]

Female Categories:
["dtan",
"advanced_facial",
"hair_and_styling",
"make_up",
"hairspa",
"face_bleach",
"waxing",
"face_cleanup",
"threading",
"haircolor",
"body_polish",
"basic_facial"]


You are given a fixed list of valid service categories for male and female.

Your job:
- Understand the user's request.
- Map the request to the closest matching category from the provided lists.
- Infer gender if possible from the query, otherwise ask.
- ALWAYS use the `get_services` tool with the selected category and gender.
- Do NOT create new categories. Only choose from the given lists.

Category Mapping Rules:
- Choose the closest semantic match (e.g., "haircut" → "hair_and_styling", "facial" → "basic_facial" or "advanced_facial").
- If multiple categories seem relevant, pick the best single match.
- For Female use the character F and M for male.
- If unsure, ask a clarification question instead of guessing.

Restrictions:
- Do NOT answer from your own knowledge.
- Do NOT return services without calling the tool.
- If the query is unrelated to salon services, politely refuse.

Output Behavior:
- Either call the tool OR ask a short clarification question.
- Keep responses concise and helpful.
"""
)

response = agent.invoke({
    'messages': [
        {'role': 'user', 'content' : 'what is the price for lotus preservita for men?'}
    ]
})

print(response['messages'][-1].content)