from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from orchestrator.router import orchestrate
from config.logger import logging
import asyncio
from messaging.phone_alert import alert_staff
from messaging.whatsapp import send_later

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
        # Persistent task (continues even if timeout)
        task = asyncio.create_task(
            orchestrate(user_number, incoming_msg)
        )

        # Enforce timeout
        texts = await asyncio.wait_for(
            asyncio.shield(task),
            timeout=12
        )
    
        # Completed within timeout
        resp = MessagingResponse()
        resp.message(texts)
        return Response(content=str(resp), media_type="application/xml")

    # If timeout, run in background
    except asyncio.TimeoutError:
        logger.error("Response timed out > 12s, continuing in background")
        async def background_handler():
            try:
                texts=await task
                send_later(texts,user_number)

            except Exception:
                alert_staff(user_number, 'chatbot_failure')
                texts = "Sorry, our auto-chat is facing some issues. This has been flagged and our staff will reach out to you or please try again later. \n\n" \
                "If urgent, please call us on +91-4534853839 (working hours : 9:00AM to 9:00PM)."
                send_later(texts,user_number)
            
        asyncio.create_task(background_handler())

        # Return temp empty message
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )