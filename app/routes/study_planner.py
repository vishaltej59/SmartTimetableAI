import streamlit as st
import pandas as pd
import plotly.express as px
from app.services.exam_service import get_exams
from app.services.planner_service import generate_study_plan
from app.services.calendar_service import create_event, check_schedule_conflicts
from app.services.study_progress_service import (
    add_study_session,
    delete_planned_sessions_for_exam,
)
from datetime import datetime


def render_study_planner():
    st.header("Smart Exam Study Planner")
    st.write(
        "Generate intelligent study plans that map directly to your free calendar slots."
    )

    exams = get_exams(st.session_state.current_user["id"])
    if not exams:
        st.info("No exams found. Add exams in the Exams tab first.")
        return

    st.subheader("Your Upcoming Exams")

    for exam in exams:
        with st.expander(
            f"{exam['subject']} (Date: {exam['exam_date']} | Prep Hours: {exam['preparation_hours']})"
        ):
            # If the user has just scheduled events, show Success Dashboard
            if st.session_state.get(f"scheduled_success_{exam['id']}"):
                st.success("✅ Sessions Created\n✅ Events Successfully Verified")
                st.write("### Scheduling Success Dashboard")
                st.dataframe(st.session_state[f"scheduled_df_{exam['id']}"])
                if st.button("Generate New Plan", key=f"reset_{exam['id']}"):
                    st.session_state.pop(f"plan_{exam['id']}", None)
                    st.session_state.pop(f"scheduled_success_{exam['id']}", None)
                    st.session_state.pop(f"scheduled_df_{exam['id']}", None)
                    st.rerun()
                continue

            if st.button(
                f"Generate Plan for {exam['subject']}", key=f"gen_plan_{exam['id']}"
            ):
                with st.spinner("Analyzing calendar and generating plan..."):
                    plan = generate_study_plan(exam["id"])

                    if "error" in plan:
                        st.error(plan["error"])
                    else:
                        st.session_state[f"plan_{exam['id']}"] = plan

            # Check if plan exists in session state to persist it during button clicks
            plan = st.session_state.get(f"plan_{exam['id']}")

            if plan:
                stats = plan.get("statistics", {})
                comp_pct = stats.get("completion_percentage", 0.0)

                # 2. Visual Progress Tracking
                st.write("### Planner Progress")
                st.progress(min(int(comp_pct), 100))
                st.write(
                    f"**{comp_pct}% Complete** | {plan['hours_scheduled']} / {plan['total_prep_hours_needed']} Hours Scheduled"
                )

                # 8. Planner Health Indicators
                status = plan["status"]
                if status == "SUCCESS":
                    st.success(
                        "Study plan fully generated! All required hours scheduled."
                    )
                elif status == "PARTIAL":
                    st.warning(
                        f"Missing {plan['hours_missing']} hours. Could only schedule {plan['hours_scheduled']} hours before the exam."
                    )
                elif status == "FAILED":
                    st.error(
                        "Failed to schedule any study hours. Your calendar might be fully booked."
                    )

                if plan.get("warning"):
                    (
                        st.error(plan["warning"])
                        if "past" in plan["warning"].lower()
                        else st.warning(plan["warning"])
                    )

                # 6. Study Analytics
                if stats:
                    st.write("---")
                    st.write("### Study Analytics")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Sessions", stats.get("total_sessions", 0))
                    col2.metric(
                        "Avg Length", f"{stats.get('average_session_length', 0)}h"
                    )
                    col3.metric("Break Time", f"{stats.get('break_time_added', 0)}h")
                    col4.metric(
                        "Quality Score", stats.get("planner_quality_score", "N/A")
                    )

                # 7. Interactive Charts
                sessions = plan.get("proposed_sessions", [])
                if sessions:
                    st.write("---")
                    st.write("### Interactive Analytics")
                    c1, c2 = st.columns(2)

                    # Bar Chart
                    df_bar = pd.DataFrame(sessions)
                    fig_bar = px.bar(
                        df_bar,
                        x="display_date",
                        y="duration_hours",
                        title="Study Hours Per Day",
                        labels={"display_date": "Date", "duration_hours": "Hours"},
                    )
                    c1.plotly_chart(fig_bar, use_container_width=True)

                    # Pie Chart
                    df_pie = pd.DataFrame(
                        {
                            "Category": ["Scheduled", "Missing"],
                            "Hours": [plan["hours_scheduled"], plan["hours_missing"]],
                        }
                    )
                    fig_pie = px.pie(
                        df_pie,
                        values="Hours",
                        names="Category",
                        title="Scheduled vs Missing Hours",
                        color="Category",
                        color_discrete_map={"Scheduled": "green", "Missing": "red"},
                    )
                    c2.plotly_chart(fig_pie, use_container_width=True)

                # 6. Expandable Debug Section
                with st.expander("[Planner Debug]"):
                    st.write(f"Exam Date: {exam['exam_date']}")
                    st.write(f"Today's Date: {datetime.now().date().isoformat()}")
                    st.write(f"Free Slots Found: {len(sessions)} blocks")
                    st.write(f"Hours Requested: {plan['total_prep_hours_needed']}")
                    st.write(f"Hours Scheduled: {plan['hours_scheduled']}")
                    st.write(f"Hours Missing: {plan['hours_missing']}")

                if not sessions:
                    st.info("No available slots found to display on the timeline.")
                else:
                    st.write("---")
                    st.write("### Calendar Preview (Timeline Layout)")

                    # 5. Timeline Layout / Session Cards
                    for sess in sessions:
                        with st.container():
                            start_dt = datetime.fromisoformat(sess["start_time"])
                            end_dt = datetime.fromisoformat(sess["end_time"])
                            st.markdown(
                                f"#### 📅 {sess['display_date']} | 🕒 {start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
                            )
                            st.markdown(
                                f"**{sess['subject']}** ({sess['duration_hours']} hours)"
                            )
                            st.write("")

                    # 4. Schedule Button
                    st.write("---")
                    if st.button(
                        "Schedule All Sessions To Google Calendar",
                        key=f"schedule_{exam['id']}",
                        type="primary",
                    ):
                        with st.spinner("Scheduling and verifying events..."):
                            # Clear any existing PLANNED sessions for this exam to avoid duplicates when regenerating
                            delete_planned_sessions_for_exam(exam["id"])

                            events_created = 0
                            total_hours_scheduled = 0.0
                            scheduled_data = []

                            for sess in sessions:
                                # Conflict Check
                                conflict = check_schedule_conflicts(
                                    sess["start_time"], sess["end_time"], user_id=st.session_state.current_user["id"]
                                )
                                if conflict.get("conflict"):
                                    continue

                                # Create & Verify
                                try:
                                    created = create_event(
                                        sess["subject"],
                                        sess["start_time"],
                                        sess["end_time"],
                                        user_id=st.session_state.current_user["id"]
                                    )
                                    if created and created.get("id"):
                                        events_created += 1
                                        total_hours_scheduled += sess["duration_hours"]

                                        # Log to study_progress database
                                        add_study_session(
                                            exam["id"],
                                            sess["subject"],
                                            sess["start_time"],
                                            sess["duration_hours"],
                                        )

                                        start_dt = datetime.fromisoformat(
                                            sess["start_time"]
                                        )
                                        end_dt = datetime.fromisoformat(
                                            sess["end_time"]
                                        )
                                        scheduled_data.append(
                                            {
                                                "Date": sess["display_date"],
                                                "Start Time": start_dt.strftime(
                                                    "%I:%M %p"
                                                ),
                                                "End Time": end_dt.strftime("%I:%M %p"),
                                                "Duration": sess["duration_hours"],
                                                "Calendar Event ID": created.get("id"),
                                            }
                                        )
                                except Exception as e:
                                    st.error(f"Failed to create event: {e}")

                            # Success Dashboard Switch
                            st.session_state[f"scheduled_success_{exam['id']}"] = True
                            st.session_state[f"scheduled_df_{exam['id']}"] = (
                                pd.DataFrame(scheduled_data)
                            )
                            st.rerun()
