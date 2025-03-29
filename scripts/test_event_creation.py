from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

# Load credentials
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

# Define event details
start_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
start_time = start_time.replace(hour=10, minute=0, second=0, microsecond=0)
end_time = start_time + datetime.timedelta(hours=2)

event = {
    "summary": "Test Tattoo Appointment",
    "description": "This is a test event created manually.",
    "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Kolkata"},
    "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Kolkata"},
}

# Create event
try:
    event = service.events().insert(
        calendarId=os.getenv("GOOGLE_CALENDAR_ID"),
        body=event,
    ).execute()

    print(f"✅ Test event created: {event.get('htmlLink')}")
except Exception as e:
    print(f"❌ Error creating test event: {e}")
