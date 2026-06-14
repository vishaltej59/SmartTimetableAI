import streamlit as st
from app.database.db import get_connection
from datetime import datetime

def render_reminders():
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-size: 2em; font-weight: 800; color: #0F172A; letter-spacing: -1px; margin-bottom: 4px;">Reminders & Alerts</h2>
        <p style="color: #475569; font-size: 1.05em; margin: 0;">Track critical assignment deadlines, upcoming exams, and academic milestones in one view.</p>
    </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.current_user["id"]
    conn = get_connection()
    cursor = conn.cursor()

    # Query pending assignments
    cursor.execute(
        "SELECT * FROM assignments WHERE user_id = ? AND status = 'Pending' ORDER BY due_date ASC",
        (user_id,)
    )
    assignments = [dict(row) for row in cursor.fetchall()]

    # Query upcoming exams
    cursor.execute(
        "SELECT * FROM exams WHERE user_id = ? ORDER BY exam_date ASC",
        (user_id,)
    )
    exams = [dict(row) for row in cursor.fetchall()]
    conn.close()

    col1, col2 = st.columns(2)

    with col1:
        st.write("### 📝 Assignment Deadlines")
        if not assignments:
            st.success("🎉 All assignments completed! No pending deadlines.")
        else:
            for item in assignments:
                try:
                    due = datetime.strptime(item["due_date"], "%Y-%m-%d").date()
                    days_left = (due - datetime.now().date()).days
                    if days_left < 0:
                        urgency = f"🔴 Overdue by {abs(days_left)} days"
                    elif days_left == 0:
                        urgency = "🟠 Due Today"
                    elif days_left == 1:
                        urgency = "🟡 Due Tomorrow"
                    else:
                        urgency = f"🟢 Due in {days_left} days"
                except Exception:
                    urgency = f"Due: {item['due_date']}"

                st.markdown(
                    f"""
                    <div style="background-color: #ffffff; padding: 16px; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <h4 style="margin: 0 0 6px 0; color: #1e293b;">{item['title']}</h4>
                        <p style="margin: 0; font-size: 0.9em; color: #64748b;">
                            {urgency} | Priority: <b>{item['priority']}</b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with col2:
        st.write("### 📅 Exam Schedules")
        if not exams:
            st.info("No upcoming exams registered.")
        else:
            for item in exams:
                try:
                    exam_dt = datetime.strptime(item["exam_date"], "%Y-%m-%d").date()
                    days_left = (exam_dt - datetime.now().date()).days
                    if days_left < 0:
                        urgency = f"Exam was {abs(days_left)} days ago"
                    elif days_left == 0:
                        urgency = "🔥 Exam Today"
                    elif days_left == 1:
                        urgency = "🚨 Exam Tomorrow"
                    else:
                        urgency = f"📅 In {days_left} days"
                except Exception:
                    urgency = f"Exam Date: {item['exam_date']}"

                st.markdown(
                    f"""
                    <div style="background-color: #ffffff; padding: 16px; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <h4 style="margin: 0 0 6px 0; color: #1e293b;">{item['subject']}</h4>
                        <p style="margin: 0; font-size: 0.9em; color: #64748b;">
                            {urgency} | Prep target: <b>{item['preparation_hours']} hours</b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
