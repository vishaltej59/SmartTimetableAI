from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Gemini
client = genai.Client(
    api_key="AQ.Ab8RN6K1KJ1JPMW2erAZns_h4v6OFh3sMpsI5cjjDM8IuhXz2w"
)

# Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = Credentials.from_authorized_user_file(
    'token.json',
    SCOPES
)

service = build('calendar', 'v3', credentials=creds)

events_result = service.events().list(
    calendarId='primary',
    maxResults=5,
    singleEvents=True,
    orderBy='startTime'
).execute()

events = events_result.get('items', [])

event_text = ""

for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    event_text += f"{start} - {event['summary']}\n"

prompt = f"""
These are my upcoming calendar events:

{event_text}

Summarize them in simple English.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print(response.text)