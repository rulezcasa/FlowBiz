from langchain.tools import tool
from sqlalchemy import text
from db.psql_connection import psqlSession
import json
from typing import List

"""
    Tool to Fetch salon services filtered by category and gender.

    Args:
        category (str): Service category.
        gender (str): Target gender.

    Returns:
        str: Formatted string of matching services or a message if none found.

    Notes:
        Uses parameterized querying to avoid SQL injection.
"""


@tool(description="Return available services based on the specified category and gender", return_direct=False)
def get_services(category: List[str], gender: str) -> str:
    db = psqlSession()
    try:
        query = text("""
            SELECT service_name, price, metadata, description
            FROM profile_saloons.service_menu
            WHERE category = ANY(:category)
              AND gender = :gender
        """)

        result = db.execute(query, {
            "category": category,  # pass list directly
            "gender": gender
        })

        rows = result.fetchall()

        if not rows:
            return f"No services found for categories '{category}' and gender '{gender}'."

        formatted = []

        for r in rows:
            metadata_str = json.dumps(r.metadata) if r.metadata else "{}"

            formatted.append(
                f"Service: {r.service_name}\n"
                f"Price: {r.price}\n"
                f"Description: {r.description}\n"
                f"Metadata: {metadata_str}"
            )

        return "\n\n".join(formatted)

    finally:
        db.close()
    

