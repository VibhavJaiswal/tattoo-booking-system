from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get variables from environment
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = [os.getenv("SCOPES")]

# Authenticate using service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Connect to Google Calendar API
service = build("calendar", "v3", credentials=credentials)

# Get list of calendars
calendar_list = service.calendarList().list().execute()
print("Your Google Calendars:")
for calendar in calendar_list["items"]:
    print(f"- {calendar['summary']} ({calendar['id']})")
