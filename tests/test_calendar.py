from googleapiclient.discovery import build
from google.oauth2 import service_account

# Path to your credentials.json file
SERVICE_ACCOUNT_FILE = "C:/Users/mailv/Documents/Upwork/AI Developer for Custom Tattoo Booking and Scheduling System/tattoo-booking-ai-b1218efcac81.json"

# Define API scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]

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
