from orchestrator.router import orchestrate
from config.logger import logging
import os
from twilio.rest import Client
from dotenv import load_dotenv

'''
Twillio whatsapp functions
'''

logger = logging.getLogger(__name__)

load_dotenv()


def send_later(message, phone):
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    response = client.messages.create(
        from_='whatsapp:+14155238886',
        body=message,
        to=f'whatsapp:+91{phone}'
    )





