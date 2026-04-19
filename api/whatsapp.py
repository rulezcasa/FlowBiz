from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from orchestrator.router import orchestrate

'''
Twillio whatsapp webhook implementation
'''

router = APIRouter()

@router.post("/whatsapp/reply")
async def reply_whatsapp(request: Request):
    form_data = await request.form()
    user_number = form_data.get("From")
    incoming_msg = form_data.get("Body")

    #Extracting only the number
    user_number = user_number.replace("whatsapp:", "")
    user_number = user_number[-10:]


    # Call the orchestrator wth user message
    response= await orchestrate(user_number,incoming_msg)
    
    #Response handling
    # if isinstance(response, list) and all(isinstance(item, dict) and 'text' in item for item in response):
    #     texts = [item['text'] for item in response]
    # else:
    #     texts = response  # fallback to original

    texts=response
    print(type(texts))

    resp = MessagingResponse()
    resp.message(str(texts))

    return Response(content=str(resp), media_type="application/xml")


