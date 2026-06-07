from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = Credentials.from_authorized_user_file(
    'token.json',
    SCOPES
)

service = build('calendar', 'v3', credentials=creds)

events_result = service.events().list(
    calendarId='primary',
    maxResults=10,
    singleEvents=True,
    orderBy='startTime'
).execute()

events = events_result.get('items', [])

print("Upcoming Events:")

if not events:
    print("No upcoming events found.")
else:
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, "-", event.get('summary', 'No Title'))