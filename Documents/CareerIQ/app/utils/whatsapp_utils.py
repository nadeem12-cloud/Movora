import streamlit as st
from twilio.rest import Client

account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
auth_token = st.secrets["TWILIO_AUTH_TOKEN"]

client = Client(account_sid, auth_token)

TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"   # Twilio Sandbox number
TWILIO_WHATSAPP_TO = "whatsapp:+917621992737"   # Your verified number

def send_whatsapp_message(message):
    client = Client(account_sid,auth_token)

    msg = client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        body=message,
        to=TWILIO_WHATSAPP_TO
    )

    return msg.sid
