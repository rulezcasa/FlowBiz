from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from orchestrator.router import orchestrate
import time
from config.logger import logging
import asyncio
from api.phone_alert import alert_staff

'''
Twillio whatsapp webhook implementation
'''

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/whatsapp/reply")
async def reply_whatsapp(request: Request):
    form_data = await request.form()
    user_number = form_data.get("From")
    incoming_msg = form_data.get("Body")

    #Extracting only the number
    user_number = user_number.replace("whatsapp:", "")
    user_number = user_number[-10:]


    # Call the orchestrator wth a timeout
    try:
        # enforce timeout
        response = await asyncio.wait_for(
            orchestrate(user_number, incoming_msg),
            timeout=12
        )
        texts = response

    except asyncio.TimeoutError:
        logger.error("Response timed out > 15s")
        texts = "Sorry, our auto-chat is facing some issues. This has been flagged and our staff will reach out to you or please try again later. \n\n" \
        "If urgent, please call us on +91-4534853839 (working hours : 9:00AM to 9:00PM)."
        alert_staff(user_number, 'chatbot_failure')

    resp = MessagingResponse()
    resp.message(texts)

    return Response(content=str(resp), media_type="application/xml")


