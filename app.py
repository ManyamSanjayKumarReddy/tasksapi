import streamlit as st
import datetime
import json
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# Get Google API credentials from environment variable
CREDENTIALS_JSON = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))

# Define the scope for accessing the Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_credentials():
    """Get OAuth 2.0 credentials."""
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_config(CREDENTIALS_JSON, SCOPES)
        # Adjust the redirect URI here if necessary
        credentials = flow.run_local_server(port=8501)
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
    return credentials

def list_events():
    """List upcoming events from the Google Calendar API."""
    credentials = get_credentials()
    service = build('calendar', 'v3', credentials=credentials)
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    if not events:
        return 'No upcoming events found.'
    
    events_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        events_list.append(f"{start} - {event['summary']}")
    
    return events_list

def main():
    st.title('Google Calendar Integration')
    st.write('This app lists your upcoming Google Calendar events.')

    if st.button('Authenticate and List Events'):
        events = list_events()
        if isinstance(events, str):
            st.write(events)
        else:
            st.write('<br>'.join(events))

if __name__ == "__main__":
    main()
