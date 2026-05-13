from db.psql_connection import psqlSession
from sqlalchemy import text
from config.logger import logging
from db.redis_connection import redisSession
import json

logger = logging.getLogger(__name__)

'''
Functions to store chat messages and stream chat messages
'''


# Check if chat exists or to be created
async def get_or_create_chat(db, phone: str) -> str:
    result = await db.execute(
        text("SELECT chat_id FROM profile_saloons.chat WHERE phone = :phone"),
        {"phone": phone}
    )
    row = result.fetchone()

    if row:
        return str(row[0])

    result = await db.execute(
        text("""
            INSERT INTO profile_saloons.chat (phone, latest_timestamp)
            VALUES (:phone, NOW())
            RETURNING chat_id
        """),
        {"phone": phone}
    )

    return str(result.scalar())


# Store messages against the chat
async def store_message(phone: str, message: str, type: str) -> str:
    async with psqlSession() as db:
        try:
            chat_id = await get_or_create_chat(db, phone)

            await db.execute(
                text("""
                    INSERT INTO profile_saloons.messages (chat_id, type, message)
                    VALUES (:chat_id, :type, :message)
                """),
                {
                    "chat_id": chat_id,
                    "type": type,
                    "message": message,
                }
            )

            await db.execute(
                text("""
                    UPDATE profile_saloons.chat
                    SET latest_timestamp = NOW()
                    WHERE chat_id = :chat_id
                """),
                {"chat_id": chat_id}
            )

            await db.commit()

            logger.info(f"Message stored | chat_id={chat_id}, type={type}")

            return chat_id

        except Exception:
            await db.rollback()
            logger.exception(f"Error storing message | phone={phone}, type={type}")
            raise


# Publish messages for with redis pub sub

async def publish_message(chat_id: str, phone: str, message: str, type: str):
    payload = json.dumps({
        "chat_id": chat_id,
        "phone": phone,
        "message": message,
        "type": type
    })

    await redisSession.publish(f"chat_events:{chat_id}", payload)  # chat specific
    await redisSession.publish("chat_events:all", payload)          # sidebar
    logger.info(f"Published SSE event | chat_id={chat_id}, type={type}")