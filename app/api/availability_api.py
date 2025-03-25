from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.core.auth import check_api_key # ✅ CORRECT
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import datetime
import pytz

router = APIRouter()

@router.get("/available_slots/")
async def get_available_slots(api_key: str = Depends(check_api_key)):
    try:
        SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)

        # Define working hours and duration
        date_to_check = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).date() + datetime.timedelta(days=1)
        working_hours = [(10, 0), (18, 0)]  # 10 AM to 6 PM
        session_duration = datetime.timedelta(hours=1.5)

        start_time = datetime.datetime.combine(date_to_check, datetime.time(*working_hours[0]), tzinfo=pytz.timezone("Asia/Kolkata"))
        end_time = datetime.datetime.combine(date_to_check, datetime.time(*working_hours[1]), tzinfo=pytz.timezone("Asia/Kolkata"))

        # Build list of possible slots
        available_slots = []
        current_time = start_time
        while current_time + session_duration <= end_time:
            slot_end = current_time + session_duration

            events = service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=current_time.astimezone(pytz.utc).isoformat(),
                timeMax=slot_end.astimezone(pytz.utc).isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            overlapping = [
                e for e in events.get("items", [])
                if "dateTime" in e["start"] and "dateTime" in e["end"]
            ]

            # Skip long-duration background events
            is_conflict = False
            for e in overlapping:
                s = datetime.datetime.fromisoformat(e["start"]["dateTime"])
                f = datetime.datetime.fromisoformat(e["end"]["dateTime"])
                if (f - s).total_seconds() > 86400:
                    continue
                is_conflict = True

            if not is_conflict:
                available_slots.append(current_time.strftime("%Y-%m-%d %H:%M"))

            current_time += datetime.timedelta(minutes=30)

        return {"status": "success", "available_slots": available_slots}
    except Exception as e:
        print("🔥 Error in /available_slots/:", str(e))
        raise e  # Re-raise to see full traceback in terminal
