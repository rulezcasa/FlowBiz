from db.redis_connection import redisSession
from db.psql_connection import psqlSession
from sqlalchemy import text
import json
from config.logger import logging

logger = logging.getLogger(__name__)

"""
    State management functions to CRUD data into Redis and PSQL
"""


# Fetch Persistent data : psql
async def lookup_customer_data(phone):
    async with psqlSession() as db:
        try:
            query = text("""
                SELECT user_id, phone, name, gender
                FROM profile_saloons.customer_data
                WHERE phone = :phone
            """)

            result = await db.execute(query, {"phone": phone})
            row = result.mappings().fetchone()

            if not row:
                insert_query = text("""
                    INSERT INTO profile_saloons.customer_data (phone)
                    VALUES (:phone)
                    ON CONFLICT (phone) DO NOTHING
                """)

                await db.execute(insert_query, {"phone": phone})
                await db.commit()

                result = await db.execute(query, {"phone": phone})
                row = result.mappings().fetchone()

            if not row:
                raise RuntimeError("Customer record could not be created or fetched")

            customer_data = {
                "user_id": str(row["user_id"]) if row["user_id"] else None,
                "phone": row["phone"],
                "name": row["name"],
                "gender": row["gender"],
            }

            logger.debug(
                f"Customer Data Fetched | user_id={row['user_id']}, phone={row['phone']}, name={row['name']}, gender={row['gender']}"
            )

            logger.info(f"Customer fetched | user_id={row['user_id']}")

            return customer_data

        except Exception:
            logger.exception("Error in lookup_customer_data")
            raise


# Update psql database with persistent fields
async def update_customer_data(updated_state):
    async with psqlSession() as db:
        try:
            entities = updated_state.get("entities", {})

            name_value = entities.get("name")
            gender_value = entities.get("gender")
            user_id = updated_state.get("user_id")

            logger.debug(
                f"Update values | user_id={user_id}, name={name_value}, gender={gender_value}"
            )

            query = text("""
                UPDATE profile_saloons.customer_data
                SET 
                    name = COALESCE(:name, name),
                    gender = COALESCE(:gender, gender)
                WHERE user_id = :user_id
            """)

            logger.debug("Executing UPDATE query")

            await db.execute(
                query,
                {
                    "name": name_value,
                    "gender": gender_value,
                    "user_id": user_id
                }
            )

            await db.commit()

            logger.info(f"Customer updated successfully | user_id={user_id}")

        except Exception:
            logger.exception("Error updating customer data. Rolling back.")
            await db.rollback()
            raise


# Fetch state from redis
async def get_state(phone):
    customer_data = await lookup_customer_data(phone)
    key = f"customers:{customer_data['phone']}:state"

    # If state exists in redis
    existing = await redisSession.get(key)
    if existing:
        logger.info(f"Redis HIT | user_id={customer_data['user_id']}. Returning state")
        logger.debug(f"Existing state: | state={existing}")
        return json.loads(existing)

    logger.info(f"Redis MISS | user_id={customer_data['user_id']}. Building state")

    # If state missing in redis - build
    state = {
        "user_id": customer_data["user_id"],
        "phone": customer_data["phone"],
        "active_agent": None,
        "active_flow": None,
        "entities": {"name": customer_data["name"], "gender": customer_data["gender"]},
        "user_message": None,
    }

    # and set
    await redisSession.set(key, json.dumps(state), ex=86400)  # TTL of 2 days

    logger.debug(f"Built state : | state={state}")
    return state


# Update state in redis
async def update_state(phone, updated_state):

    # Update customer data is called only when either of the relevant fields are persistent, otherwise avoids it.
    entities = updated_state.get("entities", {})

    if any(entities.get(k) is not None for k in ["name", "gender"]):
        logger.info(
            f"Persistent fields detected. Updating DB | user_id={updated_state['user_id']}"
        )
        await update_customer_data(updated_state)

    key = f"customers:{phone}:state"

    # Fetch existing state
    existing_raw = await redisSession.get(key)
    existing_state = json.loads(existing_raw) if existing_raw else {}

    # Merge (only updated/new fields) (SHALLOW UPDATE : only upper level keys are merged, lower level keys are fully replaced)
    merged_state = {**existing_state, **updated_state}

    # Required fields (Validating existence of critical fields)
    required_fields = [
        "user_id",
        "phone",
        "active_agent",
        "active_flow",
        "entities",
        "user_message",
    ]

    for field in required_fields:
        if field not in merged_state:
            raise ValueError(f"Missing required field in state after update: {field}")

    # None handling (Validating user_id and phone cannot be None)
    if merged_state["user_id"] is None or merged_state["phone"] is None:
        raise ValueError("user_id and phone cannot be None")

    # Save the merged state onto Redis
    await redisSession.set(key, json.dumps(merged_state), ex=86400)

    logger.info(f"Redis state updated | user_id={merged_state['user_id']}")

    return merged_state
