from datetime import datetime

def extract_text(response):
    content = response["messages"][-1].content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        # find first text block
        for block in content:
            if isinstance(block, dict) and "text" in block:
                return block["text"]

    return ""


# Utility Function - Convert timestamp to day of the week
def timestamp_to_day_of_week(timestamp: str) -> int:
    dt = datetime.fromisoformat(timestamp)
    return (dt.weekday() + 1) % 7