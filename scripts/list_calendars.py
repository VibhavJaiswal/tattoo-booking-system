from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

load_dotenv()

# Load credentials
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Verify that the service account file is correct
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

print(f"Using Service Account: {credentials.service_account_email}")

# Connect to Google Calendar API
service = build("calendar", "v3", credentials=credentials)

# Fetch all available calendars
calendar_list = service.calendarList().list().execute()

# Print calendar names and IDs
print("Available Calendars:")
for calendar in calendar_list.get("items", []):
    print(f"- {calendar['summary']} (ID: {calendar['id']})")
