from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import common
import json
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CALENDAR_ID = "td3a89bndv18d5r66km77sbtd0@group.calendar.google.com"


def get_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../token.pickle'):
        with open('../token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials3.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def create_event(course, service):
    dt_deb, dt_end = common.get_dtdeb_dtend_from_course(course)
    event = {
        'summary': course['course'],
        'location': course['place'][6:],
        'description': course['teacher'],
        'start': {
            'dateTime': dt_deb.isoformat(),
            'timeZone': 'Europe/Paris',
        },
        'end': {
            'dateTime': dt_end.isoformat(),
            'timeZone': 'Europe/Paris',
        }
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()


courses = json.load(open('courses.json', 'r'))

service = get_service()
for course in courses:
    create_event(course, service)
