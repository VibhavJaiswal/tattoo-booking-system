from googleapiclient.discovery import build
from google.oauth2 import service_account

# Load credentials
SERVICE_ACCOUNT_FILE = r"C:/Users/mailv/Documents/Upwork/AI Developer for Custom Tattoo Booking and Scheduling System/tattoo-booking-ai-b1218efcac81.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

print(f"Using Service Account: {credentials.service_account_email}")

# Connect to Google Calendar API
service = build("calendar", "v3", credentials=credentials)

# Force-add the shared calendar to the service account's list
calendar_id = "562f35caeeb4c37c57eee9d4cd31645d6162ee60b1299f182b4b553bbb8ae933@group.calendar.google.com"  # Replace this with your actual calendar ID

try:
    service.calendarList().insert(body={"id": calendar_id}).execute()
    print(f"✅ Successfully added calendar: {calendar_id}")
except Exception as e:
    print(f"❌ Failed to add calendar: {e}")
