from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.core.auth import check_api_key
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import pytz
import datetime

router = APIRouter()

@router.get("/admin/bookings/")
async def get_all_bookings(_: str = Depends(check_api_key)):
    try:
        SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)

        now = datetime.datetime.now(pytz.utc).isoformat()

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        bookings = []
        for event in events:
            bookings.append({
                "summary": event.get("summary"),
                "description": event.get("description"),
                "start": event["start"].get("dateTime"),
                "end": event["end"].get("dateTime"),
                "id": event.get("id")
            })

        return {"status": "success", "bookings": bookings}

    except Exception as e:
        print("🔥 Error in /admin/bookings/:", str(e))
        raise e  # Re-raise to see full traceback in terminal
