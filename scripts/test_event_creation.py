from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime

# Load credentials
SERVICE_ACCOUNT_FILE = r"C:\Users\mailv\Documents\Upwork\AI Developer for Custom Tattoo Booking and Scheduling System\tattoo-booking-ai-b1218efcac81.json"
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
        calendarId="562f35caeeb4c37c57eee9d4cd31645d6162ee60b1299f182b4b553bbb8ae933@group.calendar.google.com",
        body=event,
    ).execute()

    print(f"✅ Test event created: {event.get('htmlLink')}")
except Exception as e:
    print(f"❌ Error creating test event: {e}")
