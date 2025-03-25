import os
import datetime
import pytz
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

def is_time_slot_available(selected_datetime, session_duration):
    try:
        SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

        print(f"📅 Checking availability for calendar: {CALENDAR_ID}")
        print(f"🔁 Session Duration: {session_duration} hours")
        print(f"🕒 User Selected Datetime: {selected_datetime}")

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)

        # Convert user input to aware datetime in Asia/Kolkata
        local_tz = pytz.timezone("Asia/Kolkata")
        start_time = local_tz.localize(datetime.datetime.fromisoformat(selected_datetime))
        end_time = start_time + datetime.timedelta(hours=session_duration)

        # Convert to UTC for API
        time_min = start_time.astimezone(pytz.utc).isoformat()
        time_max = end_time.astimezone(pytz.utc).isoformat()

        print(f"⏱ Query Start Time (UTC): {time_min}")
        print(f"⏱ Query End Time   (UTC): {time_max}")

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        print(f"📋 Found {len(events)} overlapping event(s).")
        if events:
            for event in events:
                print("🗓 Overlapping Event:")
                print(f"   - Summary: {event.get('summary')}")
                print(f"   - Start:   {event['start'].get('dateTime')}")
                print(f"   - End:     {event['end'].get('dateTime')}")

        # ✅ Filter out long-duration events (e.g., placeholder or all-day)
        filtered_events = []
        for event in events:
            start = event.get("start", {}).get("dateTime")
            end = event.get("end", {}).get("dateTime")

            if start and end:
                start_dt = datetime.datetime.fromisoformat(start)
                end_dt = datetime.datetime.fromisoformat(end)
                duration = end_dt - start_dt

                # Ignore events longer than 1 day
                if duration.total_seconds() > 86400:
                    print(f"⏩ Ignoring long event: {start} to {end}")
                    continue

                filtered_events.append(event)

        print(f"📋 After filtering, {len(filtered_events)} event(s) overlap the requested time.")

        return len(filtered_events) == 0

    except Exception as e:
        print(f"❌ Error in calendar check: {e}")
        return {"error": "Internal server error"}
