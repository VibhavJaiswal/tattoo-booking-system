import os
import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from app.core.config import GOOGLE_CALENDAR_CREDENTIALS, GOOGLE_CALENDAR_ID

def create_calendar_event(session_time, user_selected_datetime):
    try:
        if not GOOGLE_CALENDAR_CREDENTIALS or not os.path.exists(GOOGLE_CALENDAR_CREDENTIALS):
            return {"error": "Google Calendar credentials file missing or incorrect path."}

        if not GOOGLE_CALENDAR_ID:
            return {"error": "Google Calendar ID missing from environment variables."}

        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CALENDAR_CREDENTIALS, scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)

        start_time = datetime.datetime.fromisoformat(user_selected_datetime)
        end_time = start_time + datetime.timedelta(hours=session_time)

        event = {
            "summary": "Tattoo Appointment",
            "description": f"Tattoo session estimated for {session_time} hours.",
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Kolkata"},
        }

        event = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()

        return {
            "event_id": event.get("id"),
            "booking_link": event.get("htmlLink")
        }

    except Exception as e:
        error_message = f"❌ Error Creating Calendar Event: {e}"
        print(error_message)
        return {"error": error_message}
