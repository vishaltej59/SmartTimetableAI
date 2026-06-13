from app.config import Config

from googleapiclient.discovery import build
import logging
from app.services.auth_service import authenticate_google


def get_calendar_service(user_id="default"):
    creds = authenticate_google(user_id)
    return build("calendar", "v3", credentials=creds)


def get_calendar_list(user_id="default"):
    service = get_calendar_service(user_id)
    calendar_list = service.calendarList().list().execute()
    return calendar_list.get("items", [])


def get_upcoming_events(max_results=5, user_id="default"):
    import datetime

    service = get_calendar_service(user_id)
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])


def check_schedule_conflicts(proposed_start, proposed_end, user_id="default"):
    service = get_calendar_service(user_id)

    logging.info(
        f"\n[CONFLICT CHECK] Checking conflicts from {proposed_start} to {proposed_end}..."
    )

    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=proposed_start,
                timeMax=proposed_end,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        if events:
            conflicting_event = events[0]
            title = conflicting_event.get("summary", "Busy")
            start = conflicting_event.get("start", {}).get(
                "dateTime", conflicting_event.get("start", {}).get("date")
            )
            end = conflicting_event.get("end", {}).get(
                "dateTime", conflicting_event.get("end", {}).get("date")
            )

            logging.info(
                f"[CONFLICT FOUND] Overlap with '{title}' from {start} to {end}"
            )
            return {
                "conflict": True,
                "event_title": title,
                "event_start": start,
                "event_end": end,
            }
        else:
            logging.info("[NO CONFLICT] The slot is free.")
            return {"conflict": False}
    except Exception as e:
        logging.error(f"[ERROR] Conflict check failed: {e}")
        # If API fails, default to true to prevent blind booking, or raise
        raise e


def create_event(
    summary, start_time, end_time, description="", timezone=Config.TIMEZONE, user_id="default"
):
    service = get_calendar_service(user_id)
    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_time,
            "timeZone": timezone,
        },
    }
    try:
        logging.info(
            f"\n[GOOGLE API REQUEST] Inserting event into primary calendar: {event}"
        )
        created_event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )

        event_id = created_event.get("id")
        if not event_id:
            raise Exception("No Event ID returned from API during creation.")

        logging.info(f"[GOOGLE API RESPONSE] Success. Event ID: {event_id}")
        logging.info(f"[VERIFICATION] Fetching event {event_id} from API...")

        # Phase 4: Strict Event Verification
        verified_event = (
            service.events().get(calendarId="primary", eventId=event_id).execute()
        )

        if not verified_event or verified_event.get("status") != "confirmed":
            raise Exception(
                f"Event verification failed! Fetched status: {verified_event.get('status')}"
            )

        logging.info("[EVENT VERIFIED] The event successfully exists in the calendar.")

        # --- GOOGLE CALENDAR DEBUG REPORT ---
        try:
            cal_info = service.calendars().get(calendarId="primary").execute()
            user_email = cal_info.get("id")
            cal_summary = cal_info.get("summary")

            logging.info("\n=================================")
            logging.info("GOOGLE CALENDAR DEBUG REPORT")
            logging.info("=================================")
            logging.info("\nAuthenticated User Email:")
            logging.info(user_email)
            logging.info("\nCalendar ID Used:")
            logging.info("primary")
            logging.info("\nCreated Event ID:")
            logging.info(verified_event.get("id"))
            logging.info("\nCreated Event Title:")
            logging.info(verified_event.get("summary"))
            logging.info("\nGoogle HTML Link:")
            logging.info(verified_event.get("htmlLink"))
            logging.info("\nGoogle Event Status:")
            logging.info(verified_event.get("status"))
            logging.info("\n=================================\n")
        except Exception as report_err:
            logging.info(f"Failed to generate debug report: {report_err}")

        return verified_event
    except Exception as e:
        logging.error(f"[ERROR] {e}")
        raise e


def update_event(
    event_id,
    summary=None,
    start_time=None,
    end_time=None,
    description=None,
    timezone=Config.TIMEZONE,
    user_id="default",
):
    service = get_calendar_service(user_id)
    event = service.events().get(calendarId="primary", eventId=event_id).execute()

    if summary:
        event["summary"] = summary
    if description:
        event["description"] = description
    if start_time:
        event["start"]["dateTime"] = start_time
        event["start"]["timeZone"] = timezone
    if end_time:
        event["end"]["dateTime"] = end_time
        event["end"]["timeZone"] = timezone

    updated_event = (
        service.events()
        .update(calendarId="primary", eventId=event_id, body=event)
        .execute()
    )
    return updated_event


def delete_event(event_id, user_id="default"):
    service = get_calendar_service(user_id)
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return True
