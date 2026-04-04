from db.redis_connection import redisSession
from db.psql_connection import psqlSession
from sqlalchemy import text
import json

"""
    State management functions to CRUD data into Redis and PSQL

    To do:
        - Update persistent fields in psql
"""

# Fetch Persistent data : psql  
def lookup_customer_data(phone):
    db=psqlSession()
    try:
        # If customer exists
        query = text("""
            SELECT user_id, phone, name, last_service
            FROM profile_saloons.customer_data
            WHERE phone = :phone
        """)

        result = db.execute(query, {"phone": phone}).mappings()
        row = result.fetchone()

        if not row:
            # If customer doesn't exist
            insert_query = text("""
                INSERT INTO profile_saloons.customer_data (phone)
                VALUES (:phone)
                ON CONFLICT (phone) DO NOTHING
            """)

            db.execute(insert_query, {"phone": phone})
            db.commit()  # commit for changes to be reflected

            result = db.execute(query, {"phone": phone}).mappings()
            row = result.fetchone()

        customer_data = {
            "user_id": str(row["user_id"]),
            "phone": row["phone"],
            "name": row["name"],
            "last_service": row["last_service"]
            }
        
        return customer_data
    
    finally:
        db.close()

# # Function to update persistent fields into psql
# def update_customer_data():


# Fetch state from redis
def get_state(phone):
    customer_data = lookup_customer_data(phone)
    key = f"customers:{customer_data['phone']}:state"

    # If state exists in redis
    existing = redisSession.get(key)
    if existing:
        return json.loads(existing)

    # If state missing in redis - build
    state = {
        "user_id": customer_data["user_id"],
        "phone": customer_data["phone"],
        "active_agent": None,
        "active_flow": None,
        "flow_locked": False,
        "entities": {
            "name": customer_data["name"],
            "last_service": customer_data["last_service"]
        },
        "user_message": None
    }

    # and set
    redisSession.set(
        key,
        json.dumps(state),
    )

    return state



# Update state in redis 
def update_state(phone, updated_state):

    key = f"customers:{phone}:state"

    # Fetch existing state 
    existing_raw = redisSession.get(key)
    existing_state = json.loads(existing_raw) if existing_raw else {}

    # Merge (only updated/new fields)
    merged_state = {**existing_state, **updated_state}

    # Required fields (Validating existence of critical fields)
    required_fields = [
        "user_id",
        "phone",
        "active_agent",
        "active_flow",
        "flow_locked",
        "entities",
        "user_message"
    ]

    for field in required_fields:
        if field not in merged_state:
            raise ValueError(f"Missing required field in state after update: {field}")

    # None handling (Validating user_id and phone cannot be None)
    if merged_state["user_id"] is None or merged_state["phone"] is None:
        raise ValueError("user_id and phone cannot be None")

    # Save the merged state onto Redis
    redisSession.set(key, json.dumps(merged_state))

    return merged_state







