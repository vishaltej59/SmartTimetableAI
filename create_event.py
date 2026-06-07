from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = Credentials.from_authorized_user_file(
    'token.json',
    SCOPES
)

service = build('calendar', 'v3', credentials=creds)

event = {
    'summary': 'Project Meeting',
    'start': {
        'dateTime': '2026-06-07T10:00:00+05:30',
        'timeZone': 'Asia/Kolkata',
    },
    'end': {
        'dateTime': '2026-06-07T11:00:00+05:30',
        'timeZone': 'Asia/Kolkata',
    },
}

created_event = service.events().insert(
    calendarId='primary',
    body=event
).execute()

print("Event Created!")
print(created_event.get('htmlLink'))