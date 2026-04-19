from langchain.tools import tool
from sqlalchemy import text
from db.psql_connection import psqlSession
from typing import List
from datetime import datetime
from config.logger import logging

logger = logging.getLogger(__name__)

'''
Tools for appointment scheduling

    Flow :
        1. get_service_data : Fetches service_id and and duration for the requested service via (category+gender) matching.
        2. check_availability : Fetches available stylists for the requested time slot
        3. create_appointment : Inserts appointment record and schedules it.

    Notes:
        1. Uses time only for checking stylist schedule and timestamp for appointment conflict check
        2. day_of_week mapped as (sunday to saturday : 0 to 1)
'''


# Given the category and gender, returns the service_id and duration for appointment scheduling
@tool(description="Return service_id and duration based on the specified category and gender", return_direct=False)
async def get_service_data(category: List[str], gender: str) -> str:
    # Normalize input
    if isinstance(category, str):
        category = [category]

    async with psqlSession() as db:
        try:
            query = text("""
                SELECT service_id, duration, service_name, description, price
                FROM profile_saloons.service_menu
                WHERE category = ANY(:category)
                  AND gender = :gender
            """)

            result = await db.execute(query, {
                "category": category,
                "gender": gender
            })

            rows = result.mappings().all()

            if not rows:
                return f"No services found for categories {category} and gender '{gender}'."

            formatted = []
            for r in rows:
                formatted.append(
                    f"Service_id: {r['service_id']}\n"
                    f"Duration: {r['duration']}\n"
                    f"service_name: {r['service_name']}\n"
                    f"description: {r['description']}\n"
                    f"price: {r['price']}\n"
                )

            return "\n\n".join(formatted)

        except Exception:
            logger.exception("Error fetching service data")
            raise


# Given the start_time and end_time (LLM computed) returns the list of stylists available (List[stylist_ids])
@tool(description="Get available stylist ids for a given time slot", return_direct=False)
async def check_availability(start_time: str, end_time: str, day_of_week: int) -> List[str]:
    start_time_obj = datetime.fromisoformat(start_time)
    end_time_obj = datetime.fromisoformat(end_time)

    start_time_only = start_time_obj.time()
    end_time_only = end_time_obj.time()

    async with psqlSession() as db:
        try:
            query = text("""
                SELECT ss.stylist_id
                FROM profile_saloons.stylist_schedule ss
                WHERE ss.day_of_week = :day_of_week

                  AND ss.work_start <= :start_time_only
                  AND ss.work_end   >= :end_time_only

                  AND NOT EXISTS (
                      SELECT 1
                      FROM profile_saloons.appointment_data ad
                      WHERE ad.stylist_id = ss.stylist_id
                        AND ad.status = 'booked'
                        AND ad.start_time < :end_time_ts
                        AND ad.end_time   > :start_time_ts
                  )
            """)

            result = await db.execute(query, {
                "day_of_week": day_of_week,
                "start_time_only": start_time_only,
                "end_time_only": end_time_only,
                "start_time_ts": start_time_obj,
                "end_time_ts": end_time_obj
            })

            rows = result.scalars().all()

            return [str(r) for r in rows]

        except Exception:
            logger.exception("Error checking availability")
            raise

# Schedules appointment with stylist_id, user_id, service_id, start_time and end_time
@tool(description="Create an appointment", return_direct=False)
async def create_appointment(
    stylist_id: str,
    user_id: str,
    service_id: str,
    start_time: str,
    end_time: str
) -> str:
    async with psqlSession() as db:
        try:
            query = text("""
                INSERT INTO profile_saloons.appointment_data (
                    stylist_id,
                    user_id,
                    service_id,
                    start_time,
                    end_time,
                    status
                )
                VALUES (
                    :stylist_id,
                    :user_id,
                    :service_id,
                    :start_time,
                    :end_time,
                    'booked'
                )
                RETURNING appointment_id
            """)

            result = await db.execute(query, {
                "stylist_id": stylist_id,
                "user_id": user_id,
                "service_id": service_id,
                "start_time": start_time,
                "end_time": end_time
            })

            appointment_id = result.scalar()

            await db.commit()

            logger.info(
                f"Appointment created successfully | user_id={user_id}, appointment_id={appointment_id}"
            )

            return str(appointment_id)

        except Exception:
            logger.exception(f"Error creating appointment | user_id={user_id}")
            await db.rollback()
            raise