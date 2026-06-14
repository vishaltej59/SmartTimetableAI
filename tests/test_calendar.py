from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

if __name__ == '__main__':
    import os
    import glob
    try:
        token_path = 'credentials/token.json'
        if not os.path.exists(token_path):
            token_files = glob.glob('credentials/token_*.json')
            if token_files:
                token_path = token_files[0]
                print(f"Using credentials file: {token_path}")
            else:
                raise FileNotFoundError("No Google token found under credentials/ directory. Please run the app and authenticate first.")

        creds = Credentials.from_authorized_user_file(
            token_path,
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
    except Exception as e:
        print(f"Error: {e}")