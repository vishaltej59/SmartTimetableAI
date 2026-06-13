from app.config import Config
from datetime import datetime, timedelta
import pytz


def parse_gcal_time(time_dict):
    """Parse Google Calendar time dictionary into datetime object."""
    if "dateTime" in time_dict:
        # Format: '2026-06-07T10:00:00+05:30'
        return datetime.fromisoformat(time_dict["dateTime"])
    elif "date" in time_dict:
        # All day event, return start of day in UTC
        date = datetime.fromisoformat(time_dict["date"])
        return date.replace(tzinfo=pytz.UTC)
    return None


def find_free_slots(
    events,
    required_duration_hours,
    start_date=None,
    end_date=None,
    work_start_hour=9,
    work_end_hour=21,
    timezone=Config.TIMEZONE,
):
    """
    Find free slots in a calendar given existing events.
    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)

    if start_date is None:
        start_date = now
    else:
        if start_date.tzinfo is None:
            start_date = tz.localize(start_date)

    if end_date is None:
        end_date = start_date + timedelta(days=7)  # Look ahead 7 days by default
    else:
        if end_date.tzinfo is None:
            end_date = tz.localize(end_date)

    required_duration = timedelta(hours=required_duration_hours)

    # Parse and filter events within range
    parsed_events = []
    for event in events:
        start = parse_gcal_time(event["start"])
        end = parse_gcal_time(event["end"])

        if start and end and end > start_date and start < end_date:
            parsed_events.append((start, end))

    # Sort events by start time
    parsed_events.sort(key=lambda x: x[0])

    # Merge overlapping events
    merged_events = []
    for event in parsed_events:
        if not merged_events:
            merged_events.append(event)
        else:
            last_start, last_end = merged_events[-1]
            if event[0] <= last_end:
                merged_events[-1] = (last_start, max(last_end, event[1]))
            else:
                merged_events.append(event)

    # Find free slots day by day
    free_slots = []
    current_day = start_date

    while current_day.date() <= end_date.date():
        # Define working hours for the day
        day_start = current_day.replace(
            hour=work_start_hour, minute=0, second=0, microsecond=0
        )
        day_end = current_day.replace(
            hour=work_end_hour, minute=0, second=0, microsecond=0
        )

        # If it's today, we can't start before 'now'
        if day_start < now:
            day_start = now

        if day_start >= day_end:
            current_day += timedelta(days=1)
            continue

        current_time = day_start

        for e_start, e_end in merged_events:
            # Event is entirely before our current time
            if e_end <= current_time:
                continue

            # Event starts after current day ends
            if e_start >= day_end:
                break

            # Check gap before event
            if e_start > current_time:
                gap = e_start - current_time
                if gap >= required_duration:
                    free_slots.append((current_time, e_start))

            # Move current_time to end of event
            current_time = max(current_time, e_end)

        # Check remaining time in the day
        if current_time < day_end:
            gap = day_end - current_time
            if gap >= required_duration:
                free_slots.append((current_time, day_end))

        current_day += timedelta(days=1)

    # Format output for LLM readability
    result = []
    for start, end in free_slots:
        result.append(f"{start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%H:%M')}")

    return result
