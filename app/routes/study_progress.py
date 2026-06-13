import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from app.services.exam_service import get_exams
from app.services.study_progress_service import (
    get_sessions_for_exam,
    get_all_study_sessions,
    update_session_status,
    get_exam_readiness,
)


def render_study_progress():
    st.header("Study Progress Dashboard")
    st.write("Track your study sessions and overall exam readiness.")

    exams = get_exams(st.session_state.current_user["id"])
    if not exams:
        st.info("No exams found. Add exams in the Exams tab first.")
        return

    all_sessions = get_all_study_sessions(st.session_state.current_user["id"])

    # 6. Analytics Overview
    st.subheader("Analytics Overview")
    total_planned = sum(s["planned_hours"] for s in all_sessions)
    total_completed = sum(
        s["completed_hours"] for s in all_sessions if s["status"] == "COMPLETED"
    )
    total_missed = sum(
        s["planned_hours"] for s in all_sessions if s["status"] == "MISSED"
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Planned Hours", f"{total_planned:.1f}h")
    col2.metric("Completed Hours", f"{total_completed:.1f}h")
    col3.metric("Missed Hours", f"{total_missed:.1f}h")

    completion_pct = (total_completed / total_planned * 100) if total_planned > 0 else 0
    col4.metric("Overall Completion", f"{completion_pct:.1f}%")

    st.divider()

    # 7. Charts
    if all_sessions:
        st.subheader("Progress Charts")
        c1, c2 = st.columns(2)

        # Completed vs Remaining (Pie Chart)
        df_pie = pd.DataFrame(
            {
                "Status": ["Completed", "Remaining/Missed"],
                "Hours": [total_completed, max(0, total_planned - total_completed)],
            }
        )
        fig_pie = px.pie(
            df_pie,
            values="Hours",
            names="Status",
            title="Completed vs Remaining Hours",
            hole=0.3,
        )
        c1.plotly_chart(fig_pie, use_container_width=True)

        # Hours Studied Per Day (Bar Chart)
        completed_sessions = [s for s in all_sessions if s["status"] == "COMPLETED"]
        if completed_sessions:
            df_bar = pd.DataFrame(completed_sessions)
            df_bar["date"] = df_bar["session_date"].apply(
                lambda x: x[:10]
            )  # Extract YYYY-MM-DD
            daily_hours = df_bar.groupby("date")["completed_hours"].sum().reset_index()
            fig_bar = px.bar(
                daily_hours,
                x="date",
                y="completed_hours",
                title="Hours Studied Per Day",
            )
            c2.plotly_chart(fig_bar, use_container_width=True)
        else:
            c2.info("No completed sessions yet to show daily chart.")

    st.divider()

    # 4 & 5. Progress Dashboard per Exam
    st.subheader("Exam Progress")
    for exam in exams:
        required_hours = float(exam.get("preparation_hours", 0))
        readiness = get_exam_readiness(exam["id"], required_hours)
        completed = readiness["total_completed"]
        score = readiness["readiness_score"]

        # 8. Smart Alerts
        try:
            exam_date = datetime.strptime(exam["exam_date"], "%Y-%m-%d")
            days_remaining = (exam_date.date() - datetime.now().date()).days
        except ValueError:
            days_remaining = 999

        with st.expander(f"📚 {exam['subject']} - {score}% Ready", expanded=True):
            if days_remaining <= 3 and days_remaining >= 0:
                st.warning(f"⚠ Exam Within {days_remaining} Days!")
            elif days_remaining < 0:
                st.info("This exam has passed.")

            if score < 50 and days_remaining <= 7:
                st.error("⚠ Behind Schedule! Try to complete more sessions.")

            st.write(
                f"**Required Hours:** {required_hours}h | **Completed:** {completed}h | **Remaining:** {max(0, required_hours - completed)}h"
            )

            # Progress Bar
            st.progress(score / 100.0)

            # Sessions for this exam
            sessions = get_sessions_for_exam(exam["id"])
            if not sessions:
                st.info(
                    "No sessions planned yet. Go to Study Planner to generate a plan."
                )
            else:
                st.write("#### Study Sessions")
                for sess in sessions:
                    col_info, col_actions = st.columns([3, 2])

                    # Formatting date
                    try:
                        s_date = datetime.fromisoformat(sess["session_date"]).strftime(
                            "%b %d, %I:%M %p"
                        )
                    except Exception:
                        s_date = sess["session_date"]

                    with col_info:
                        status_emoji = (
                            "⏳"
                            if sess["status"] == "PLANNED"
                            else "✅" if sess["status"] == "COMPLETED" else "❌"
                        )
                        st.write(
                            f"{status_emoji} **{s_date}** - {sess['planned_hours']}h ({sess['status']})"
                        )

                    with col_actions:
                        if sess["status"] == "PLANNED":
                            c1, c2, c3 = st.columns(3)
                            if c1.button("✅ Done", key=f"done_{sess['id']}"):
                                update_session_status(
                                    sess["id"], "COMPLETED", sess["planned_hours"]
                                )
                                st.rerun()
                            if c2.button("▶ Start", key=f"start_{sess['id']}"):
                                update_session_status(sess["id"], "IN_PROGRESS")
                                st.rerun()
                            if c3.button("❌ Missed", key=f"miss_{sess['id']}"):
                                update_session_status(sess["id"], "MISSED", 0.0)
                                st.rerun()
                        elif sess["status"] == "IN_PROGRESS":
                            if st.button("✅ Mark Completed", key=f"comp_{sess['id']}"):
                                update_session_status(
                                    sess["id"], "COMPLETED", sess["planned_hours"]
                                )
                                st.rerun()
