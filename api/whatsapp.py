from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from orchestrator.router import orchestrate

router = APIRouter()

@router.post("/whatsapp/reply")
async def reply_whatsapp(request: Request):
    form_data = await request.form()
    user_number = form_data.get("From")
    incoming_msg = form_data.get("Body")

    #Extracting only the number
    user_number = user_number.replace("whatsapp:", "")
    user_number = user_number[-10:]


    response=orchestrate(user_number,incoming_msg)
    if isinstance(response, list) and all(isinstance(item, dict) and 'text' in item for item in response):
        texts = [item['text'] for item in response]
    else:
        texts = response  # fallback to original

    resp = MessagingResponse()
    resp.message(texts)

    return Response(content=str(resp), media_type="application/xml")


