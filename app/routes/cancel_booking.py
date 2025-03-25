from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from app.core.config import GOOGLE_CALENDAR_CREDENTIALS, GOOGLE_CALENDAR_ID
from app.core.auth import check_api_key
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import os

router = APIRouter()

@router.post("/cancel_booking/")
async def cancel_booking(event_id: str = Form(...), api_key: str = Depends(check_api_key)):
    try:
        if not GOOGLE_CALENDAR_CREDENTIALS or not os.path.exists(GOOGLE_CALENDAR_CREDENTIALS):
            return JSONResponse(status_code=500, content={"error": "Google Calendar credentials missing."})

        if not GOOGLE_CALENDAR_ID:
            return JSONResponse(status_code=500, content={"error": "Google Calendar ID missing."})

        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CALENDAR_CREDENTIALS,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)

        try:
            service.events().delete(calendarId=GOOGLE_CALENDAR_ID, eventId=event_id).execute()
            return {"status": "success", "message": "Appointment canceled successfully."}
        except HttpError as error:
            if error.resp.status == 410:
                return {
                    "status": "error",
                    "message": "This appointment was already deleted or no longer exists."
                }
            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Google Calendar API error: {error._get_reason()}"}
                )

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Unexpected Error: {str(e)}"})
