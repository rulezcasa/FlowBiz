from twilio.rest import Client
from dotenv import load_dotenv
import os

'''
Send alerts to staff incase of system disfunction
'''

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

def alert_staff(phone, alert_type):

    if alert_type == 'chatbot_failure':
        message_body = f"ALERT : Chatbot failure for customer: {phone}"

    elif alert_type == 'ambiguous_query':
        message_body = f"ALERT : Ambiguous query for customer: {phone}"

    elif alert_type == 'unhappy_customer':
        message_body = f"ALERT : Unhappy response for customer: {phone}"

    else:
        raise ValueError(f"Unknown alert_type: {alert_type}")

    message = client.messages.create(
        from_='+17755102130',
        body=message_body,
        to='+919035790945'
    )

