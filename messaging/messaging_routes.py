from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from fastapi.responses import StreamingResponse
from orchestrator.router import orchestrate
from config.logger import logging
import asyncio
from messaging.phone_alert import alert_staff
from messaging.whatsapp import send_later
from messaging.chat_dashboard import store_message, publish_message
from db.redis_connection import redisSession
from state.state_manager import is_bot_disabled, set_bot_status
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

    # Store and publish inbound message
    chat_id = await store_message(user_number, incoming_msg, type="inbound")
    await publish_message(chat_id, user_number, incoming_msg, type="inbound")

    if await is_bot_disabled():
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )

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

        # Store and publish outbound message
        await store_message(user_number, texts, type="outbound")
        await publish_message(chat_id, user_number, texts, type="outbound")
    
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
                await store_message(user_number, texts, type="outbound")
                await publish_message(chat_id, user_number, texts, type="outbound")
                send_later(texts,user_number)

            except Exception:
                alert_staff(user_number, 'chatbot_failure')
                texts = "Sorry, our auto-chat is facing some issues. This has been flagged and our staff will reach out to you or please try again later. \n\n" \
                "If urgent, please call us on +91-4534853839 (working hours : 9:00AM to 9:00PM)."
                await store_message(user_number, texts, type="outbound")
                await publish_message(chat_id, user_number, texts, type="outbound")
                send_later(texts,user_number)
            
        asyncio.create_task(background_handler())

        # Return temp empty message
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )




@router.get("/stream/{chat_id}")
async def stream(chat_id: str, request: Request):
    async def event_generator():
        pubsub = redisSession.pubsub()
        await pubsub.subscribe(f"chat_events:{chat_id}")
        last_message_time = asyncio.get_event_loop().time()

        try:
            while True:
                if await request.is_disconnected():
                    break

                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                if message:
                    last_message_time = asyncio.get_event_loop().time()
                    yield f"data: {message['data']}\n\n"

                elif asyncio.get_event_loop().time() - last_message_time > 30:
                    yield ": heartbeat\n\n"
                    last_message_time = asyncio.get_event_loop().time()

        finally:
            await pubsub.unsubscribe(f"chat_events:{chat_id}")
            await pubsub.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@router.get("/stream/all")
async def stream_all(request: Request):
    async def event_generator():
        pubsub = redisSession.pubsub()
        await pubsub.subscribe("chat_events:all")
        last_message_time = asyncio.get_event_loop().time()

        try:
            while True:
                if await request.is_disconnected():
                    break

                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                if message:
                    last_message_time = asyncio.get_event_loop().time()
                    yield f"data: {message['data']}\n\n"

                elif asyncio.get_event_loop().time() - last_message_time > 30:
                    yield ": heartbeat\n\n"
                    last_message_time = asyncio.get_event_loop().time()

        finally:
            await pubsub.unsubscribe("chat_events:all")
            await pubsub.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

@router.post("/dashboard/takeover")
async def takeover(bot_disabled: bool):
    await set_bot_status(disabled=bot_disabled)
    return {"bot_disabled": bot_disabled}

@router.post("/dashboard/send_message")
async def send_message(request: Request):
    body = await request.json()
    phone = body.get("phone")
    message = body.get("message")
    chat_id = body.get("chat_id")

    send_later(message, phone)

    await store_message(phone, message, type="outbound")
    await publish_message(chat_id, phone, message, type="outbound")

    return {"status": "sent"}

