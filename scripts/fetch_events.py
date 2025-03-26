from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
import os

# Load credentials
SERVICE_ACCOUNT_FILE = r"C:\Users\mailv\Documents\Upwork\AI Developer for Custom Tattoo Booking and Scheduling System\tattoo-booking-ai-b1218efcac81.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

# Define time range (list events for the next 7 days)
now = datetime.datetime.utcnow().isoformat() + "Z"
end_time = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + "Z"

events_result = service.events().list(
    calendarId=os.getenv("GOOGLE_CALENDAR_ID"),
    timeMin=now,
    timeMax=end_time,
    singleEvents=True,
    orderBy="startTime",
).execute()

events = events_result.get("items", [])

print("Upcoming Tattoo Appointments:")
if not events:
    print("❌ No upcoming events found.")
else:
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"- {event['summary']} at {start} (Event ID: {event['id']})")
