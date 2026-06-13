from app.config import Config
import math
import logging
from datetime import datetime, timedelta
import pytz
from app.services.exam_service import get_exam_by_id
from app.services.calendar_service import get_upcoming_events
from app.utils.time_utils import find_free_slots


def generate_study_plan(exam_id):
    exam = get_exam_by_id(exam_id)
    if not exam:
        return {"error": f"Exam ID {exam_id} not found."}

    subject = exam.get("subject")
    exam_date_str = exam.get("exam_date")
    prep_hours = float(exam.get("preparation_hours", 5.0))
    user_id = exam.get("user_id", "default")

    tz = pytz.timezone(Config.TIMEZONE)
    now = datetime.now(tz)

    # Parse exam date robustly
    try:
        # If it's a date string like YYYY-MM-DD
        dt_obj = datetime.strptime(exam_date_str, "%Y-%m-%d")
        exam_date = tz.localize(dt_obj)
    except ValueError:
        return {"error": f"Invalid exam date format: {exam_date_str}"}

    days_remaining = (exam_date.date() - now.date()).days

    if days_remaining < 0:
        return {"error": "Exam is in the past."}

    # Calculate daily hour distribution
    daily_hours = []

    if days_remaining == 0:
        # Exam is today: cram everything today
        daily_hours.append({"offset": 0, "hours": prep_hours})
        days_to_schedule = 1
    elif days_remaining == 1:
        # Exam is tomorrow: everything tomorrow
        daily_hours.append({"offset": 1, "hours": prep_hours})
        days_to_schedule = 1
    else:
        # Ascending weight distribution
        # e.g. 5 days remaining. We schedule on Day 1, Day 2, Day 3, Day 4, Day 5.
        weights = list(range(1, days_remaining + 1))
        total_weight = sum(weights)
        for i, w in enumerate(weights):
            day_offset = i + 1  # 1 to days_remaining
            hours = prep_hours * (w / total_weight)
            daily_hours.append({"offset": day_offset, "hours": hours})
        days_to_schedule = days_remaining

    events = get_upcoming_events(100, user_id=user_id)
    proposed_sessions = []
    hours_scheduled = 0.0
    rollover_hours = 0.0
    break_time_added = 0.0

    for day_plan in daily_hours:
        target_day = now + timedelta(days=day_plan["offset"])

        # We process this day's allocation + any rolled over hours
        target_hours_today = day_plan["hours"] + rollover_hours
        rollover_hours = 0.0

        if target_hours_today <= 0.01:
            continue

        # Cap daily study to 14 hours (8 AM - 10 PM)
        if target_hours_today > 14.0:
            rollover_hours += target_hours_today - 14.0
            target_hours_today = 14.0

        # Search for free slots on this day between 8 AM and 10 PM
        start_bound = target_day.replace(hour=8, minute=0, second=0, microsecond=0)
        end_bound = target_day.replace(hour=22, minute=0, second=0, microsecond=0)

        if start_bound < now:
            start_bound = now

        if start_bound >= end_bound:
            # Day is over, push to next day
            rollover_hours += target_hours_today
            continue

        slots = find_free_slots(
            events,
            required_duration_hours=0.5,  # Find any gap >= 30 mins
            start_date=start_bound,
            end_date=end_bound,
            work_start_hour=8,
            work_end_hour=22,
        )

        hours_to_schedule_today = target_hours_today

        for slot_str in slots:
            if hours_to_schedule_today <= 0.01:
                break

            start_str, end_time_str = slot_str.split(" to ")
            slot_start = tz.localize(datetime.strptime(start_str, "%Y-%m-%d %H:%M"))

            # Since end_time_str is just '%H:%M', we reconstruct it
            end_hour, end_minute = map(int, end_time_str.split(":"))
            slot_end_dt = slot_start.replace(hour=end_hour, minute=end_minute)

            # If the parsing crosses a day boundary due to naive replacement, fix it
            if slot_end_dt <= slot_start:
                slot_end_dt += timedelta(days=1)

            available_hours = (slot_end_dt - slot_start).total_seconds() / 3600.0
            current_start = slot_start

            # Sub-chunking loop
            while available_hours > 0.01 and hours_to_schedule_today > 0.01:
                session_dur = min(2.0, available_hours, hours_to_schedule_today)

                # Determine Study vs Revision (70/30 split based on total_prep_hours_needed)
                if hours_scheduled < 0.7 * prep_hours:
                    sess_type = "Study"
                else:
                    sess_type = "Revision"

                session_end = current_start + timedelta(hours=session_dur)

                proposed_sessions.append(
                    {
                        "subject": f"{sess_type}: {subject}",
                        "start_time": current_start.isoformat(),
                        "end_time": session_end.isoformat(),
                        "duration_hours": round(session_dur, 2),
                        "display_date": f"{current_start.strftime('%B')} {current_start.day}",
                    }
                )

                hours_scheduled += session_dur
                hours_to_schedule_today -= session_dur
                available_hours -= session_dur

                # Mandatory 15 min break
                if available_hours >= 0.25 and hours_to_schedule_today > 0.01:
                    current_start = session_end + timedelta(minutes=15)
                    available_hours -= 0.25
                    break_time_added += 0.25
                else:
                    break  # cannot fit another session + break

        # Daily Debug Output
        day_scheduled = target_hours_today - hours_to_schedule_today
        logging.info("\n[DAILY PLANNER]")
        logging.info(f"Date: {target_day.strftime('%Y-%m-%d')}")
        logging.info(f"Target Hours: {round(target_hours_today, 2)}")
        logging.info(f"Scheduled Hours: {round(day_scheduled, 2)}")
        logging.info(f"Remaining Hours: {round(hours_to_schedule_today, 2)}")

        # If we couldn't schedule all target hours today, roll them over
        if hours_to_schedule_today > 0.01:
            rollover_hours += hours_to_schedule_today

    hours_scheduled = round(hours_scheduled, 2)
    hours_missing = round(max(0, prep_hours - hours_scheduled), 2)

    if hours_scheduled >= prep_hours:
        status = "SUCCESS"
    elif hours_scheduled == 0:
        status = "FAILED"
    else:
        status = "PARTIAL"

    warning = ""
    if days_remaining <= 0:
        warning = "Exam is today or has already passed. Study plan may be incomplete."
    elif hours_missing > 0:
        warning = f"Only {hours_scheduled} of {prep_hours} hours can be scheduled before the exam."

    total_sessions = len(proposed_sessions)
    average_session = hours_scheduled / total_sessions if total_sessions > 0 else 0
    completion_percentage = (
        (hours_scheduled / prep_hours) * 100 if prep_hours > 0 else 0
    )

    if completion_percentage >= 95:
        planner_quality_score = "Excellent ⭐"
    elif completion_percentage >= 80:
        planner_quality_score = "Good 👍"
    elif completion_percentage >= 60:
        planner_quality_score = "Fair ⚠️"
    else:
        planner_quality_score = "Poor ❌"

    logging.info("\n[PLANNER]")
    logging.info(f"Exam Date: {exam_date_str}")
    logging.info(f"Today: {now.date().isoformat()}")
    logging.info(f"Days Remaining: {days_remaining}")
    logging.info(f"Hours Required: {prep_hours}")
    logging.info(f"Hours Scheduled: {hours_scheduled}")
    logging.info(f"Hours Missing: {hours_missing}")

    return {
        "exam": subject,
        "days_remaining": days_remaining,
        "total_prep_hours_needed": prep_hours,
        "hours_scheduled": hours_scheduled,
        "hours_missing": hours_missing,
        "status": status,
        "proposed_sessions": proposed_sessions,
        "warning": warning,
        "statistics": {
            "total_sessions": total_sessions,
            "average_session_length": round(average_session, 2),
            "break_time_added": round(break_time_added, 2),
            "completion_percentage": round(completion_percentage, 2),
            "planner_quality_score": planner_quality_score,
        },
    }
