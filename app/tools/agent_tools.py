from app.services.assignment_service import (
    get_assignments,
    add_assignment,
    update_assignment,
    delete_assignment,
)
import logging
from app.services.calendar_service import (
    get_upcoming_events,
    create_event,
    update_event,
    delete_event,
    check_schedule_conflicts,
)
from app.services.planner_service import generate_study_plan
from app.utils.time_utils import find_free_slots
from app.services.exam_service import get_exams, add_exam, delete_exam
import json
from datetime import datetime


def validate_iso_date(date_str):
    try:
        # Check if + or - timezone offset or Z exists
        if "+" not in date_str and "-" not in date_str[-6:] and "Z" not in date_str:
            return (
                False,
                "Missing timezone offset (e.g., +05:30). Dates must be timezone-aware.",
            )

        # If 'Z' is present, replace with +00:00 for fromisoformat in older pythons
        clean_str = date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)

        current_year = datetime.now().year
        if dt.year < current_year:
            return (
                False,
                f"Year {dt.year} is in the past. Current year is {current_year}. Please use valid future dates.",
            )

        return True, ""
    except ValueError as e:
        return False, f"Malformed ISO 8601 date string: {date_str}. Error: {e}"


GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "tool_get_assignments",
            "description": "Retrieve all assignments for the user.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_add_assignment",
            "description": "Add a new assignment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the assignment.",
                    },
                    "due_date": {
                        "type": "string",
                        "description": "The due date in YYYY-MM-DD format.",
                    },
                    "estimated_hours": {
                        "type": "number",
                        "description": "Estimated hours to complete.",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["High", "Medium", "Low"],
                        "description": "Priority.",
                    },
                },
                "required": ["title", "due_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_update_assignment",
            "description": "Update an assignment's status or title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "assignment_id": {"type": "integer"},
                    "status": {"type": "string"},
                    "title": {"type": "string"},
                },
                "required": ["assignment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_delete_assignment",
            "description": "Delete an assignment by ID.",
            "parameters": {
                "type": "object",
                "properties": {"assignment_id": {"type": "integer"}},
                "required": ["assignment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_upcoming_events",
            "description": "Fetch upcoming events from Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {"max_results": {"type": "integer"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_create_calendar_event",
            "description": "Create a new event in Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Title of the event."},
                    "start_time": {
                        "type": "string",
                        "description": "ISO 8601 format string (e.g., '2026-06-07T10:00:00+05:30').",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "ISO 8601 format string.",
                    },
                },
                "required": ["summary", "start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_check_schedule_conflicts",
            "description": "Check if a proposed time slot conflicts with existing Google Calendar events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "proposed_start": {
                        "type": "string",
                        "description": "ISO 8601 format string for proposed start time.",
                    },
                    "proposed_end": {
                        "type": "string",
                        "description": "ISO 8601 format string for proposed end time.",
                    },
                },
                "required": ["proposed_start", "proposed_end"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_delete_calendar_event",
            "description": "Delete a Google Calendar event by ID.",
            "parameters": {
                "type": "object",
                "properties": {"event_id": {"type": "string"}},
                "required": ["event_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_find_free_slots",
            "description": "Find free time slots in the user's calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration_hours": {
                        "type": "number",
                        "description": "Number of hours required.",
                    }
                },
                "required": ["duration_hours"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_add_exam",
            "description": "Add an exam.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "exam_date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD.",
                    },
                    "preparation_hours": {"type": "number"},
                },
                "required": ["subject", "exam_date", "preparation_hours"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_exams",
            "description": "Retrieve all exams for the user.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_system_diagnostics",
            "description": "Run a comprehensive health check on Google Calendar connectivity, OAuth, and API access.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_generate_study_plan",
            "description": "Generate a multi-day study plan for a specific exam ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "exam_id": {"type": "integer", "description": "The ID of the exam."}
                },
                "required": ["exam_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_batch_create_calendar_events",
            "description": "Create multiple events in Google Calendar at once.",
            "parameters": {
                "type": "object",
                "properties": {
                    "events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "summary": {"type": "string"},
                                "start_time": {
                                    "type": "string",
                                    "description": "ISO 8601",
                                },
                                "end_time": {
                                    "type": "string",
                                    "description": "ISO 8601",
                                },
                            },
                            "required": ["summary", "start_time", "end_time"],
                        },
                    }
                },
                "required": ["events"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_study_progress",
            "description": "Retrieve study progress and exam readiness score. Returns required hours, completed hours, and readiness percentage for all exams or a specific exam if exam_id is provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "exam_id": {
                        "type": "integer",
                        "description": "Optional ID of a specific exam. If omitted, returns progress for all exams.",
                    }
                },
            },
        },
    },
]


def execute_tool(function_name: str, arguments: dict):
    """Router to execute the corresponding Python function."""
    import streamlit as st
    user_id = st.session_state.current_user["id"]
    logging.info(f"\n[TOOL SELECTED] {function_name} for user {user_id}")
    try:
        if function_name == "tool_get_assignments":
            return get_assignments(user_id)
        elif function_name == "tool_add_assignment":
            return add_assignment(
                user_id,
                arguments["title"],
                arguments["due_date"],
                arguments.get("priority", "Medium"),
                arguments.get("estimated_hours", 1.0),
            )
        elif function_name == "tool_update_assignment":
            return update_assignment(
                arguments["assignment_id"],
                status=arguments.get("status"),
                title=arguments.get("title"),
            )
        elif function_name == "tool_delete_assignment":
            return delete_assignment(arguments["assignment_id"])
        elif function_name == "tool_get_upcoming_events":
            return get_upcoming_events(arguments.get("max_results", 10), user_id=user_id)
        elif function_name == "tool_create_calendar_event":
            logging.info(
                f"[EVENT CREATE REQUEST] Title: {arguments['summary']} | Start: {arguments['start_time']}"
            )

            # Phase 2 Validation
            is_valid, err_msg = validate_iso_date(arguments["start_time"])
            if not is_valid:
                return {"success": False, "error": err_msg}
            is_valid, err_msg = validate_iso_date(arguments["end_time"])
            if not is_valid:
                return {"success": False, "error": err_msg}

            try:
                event = create_event(
                    arguments["summary"], arguments["start_time"], arguments["end_time"], user_id=user_id
                )
                if event and event.get("id"):
                    event_id = event.get("id")
                    logging.info(
                        f"[SUCCESS] Event Created Successfully. Event ID: {event_id}"
                    )
                    return {
                        "success": True,
                        "event_id": event_id,
                        "link": event.get("htmlLink"),
                    }
                else:
                    logging.error(
                        f"[ERROR] Google API Event Creation Failed: No Event ID returned. Faked success detected."
                    )
                    return {
                        "success": False,
                        "error": "No Event ID returned from Google API.",
                    }
            except Exception as e:
                logging.error(f"[ERROR] Google API Event Creation Failed: {e}")
                return {"success": False, "error": str(e)}
        elif function_name == "tool_delete_calendar_event":
            return delete_event(arguments["event_id"], user_id=user_id)
        elif function_name == "tool_check_schedule_conflicts":
            # Phase 2 Validation
            is_valid, err_msg = validate_iso_date(arguments["proposed_start"])
            if not is_valid:
                return {"success": False, "error": err_msg}
            is_valid, err_msg = validate_iso_date(arguments["proposed_end"])
            if not is_valid:
                return {"success": False, "error": err_msg}

            return check_schedule_conflicts(
                arguments["proposed_start"], arguments["proposed_end"], user_id=user_id
            )
        elif function_name == "tool_find_free_slots":
            logging.info(
                f"[FIND FREE SLOT] Searching calendar for {arguments['duration_hours']} hours..."
            )
            events = get_upcoming_events(30, user_id=user_id)
            return find_free_slots(events, arguments["duration_hours"])
        elif function_name == "tool_add_exam":
            return add_exam(
                user_id,
                arguments["subject"],
                arguments["exam_date"],
                "",
                arguments["preparation_hours"],
            )
        elif function_name == "tool_get_exams":
            return get_exams(user_id)
        elif function_name == "tool_system_diagnostics":
            logging.info("\n[DIAGNOSTICS] Running health check...")
            try:
                from app.services.calendar_service import get_calendar_list

                cals = get_calendar_list(user_id=user_id)
                primary_cal = next((c for c in cals if c.get("primary")), None)
                if primary_cal:
                    logging.info("[DIAGNOSTICS] Success: Calendar access confirmed.")
                    return {
                        "status": "Healthy",
                        "auth_email": primary_cal.get("id"),
                        "can_read": True,
                        "can_write": True,  # implicitly assumed if read works on primary
                        "calendars_found": len(cals),
                    }
                else:
                    return {"status": "Warning", "error": "No primary calendar found"}
            except Exception as e:
                return {"status": "Error", "error": str(e)}
        elif function_name == "tool_generate_study_plan":
            return generate_study_plan(arguments["exam_id"])
        elif function_name == "tool_batch_create_calendar_events":
            events_added = 0
            total_hours = 0.0
            for ev in arguments.get("events", []):
                # Validation
                is_valid, err = validate_iso_date(ev["start_time"])
                if not is_valid:
                    continue
                is_valid, err = validate_iso_date(ev["end_time"])
                if not is_valid:
                    continue

                # Conflict Check internally
                conflict = check_schedule_conflicts(ev["start_time"], ev["end_time"], user_id=user_id)
                if conflict.get("conflict"):
                    continue

                try:
                    created = create_event(
                        ev["summary"], ev["start_time"], ev["end_time"], user_id=user_id
                    )
                    if created and created.get("id"):
                        events_added += 1

                        # Calculate duration
                        dt_start = datetime.fromisoformat(
                            ev["start_time"].replace("Z", "+00:00")
                        )
                        dt_end = datetime.fromisoformat(
                            ev["end_time"].replace("Z", "+00:00")
                        )
                        dur = (dt_end - dt_start).total_seconds() / 3600.0
                        total_hours += dur
                except Exception as e:
                    pass

            return f"Created {events_added} study sessions.\n\nTotal Hours:\n{round(total_hours, 2)}\n\nCalendar Events Added:\n{events_added}"
        elif function_name == "tool_get_study_progress":
            from app.services.study_progress_service import get_exam_readiness

            exams = get_exams(user_id)
            results = []
            for exam in exams:
                if (
                    "exam_id" in arguments
                    and arguments["exam_id"] is not None
                    and exam["id"] != arguments["exam_id"]
                ):
                    continue
                readiness = get_exam_readiness(
                    exam["id"], float(exam.get("preparation_hours", 0))
                )
                results.append(
                    {
                        "exam_id": exam["id"],
                        "subject": exam["subject"],
                        "required_hours": exam.get("preparation_hours", 0),
                        "completed_hours": readiness["total_completed"],
                        "readiness_score_percentage": readiness["readiness_score"],
                    }
                )
            return results
        else:
            logging.error(f"[ERROR] Unknown function: {function_name}")
            return {"error": f"Unknown function: {function_name}"}
    except Exception as e:
        logging.error(f"[ERROR] Tool execution failed: {e}")
        return {"error": str(e)}
