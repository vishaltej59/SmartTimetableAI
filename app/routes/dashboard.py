import streamlit as st
from app.services.assignment_service import get_assignments
from app.services.exam_service import get_exams
from app.database.db import get_connection
from datetime import datetime
import html

def render_dashboard():
    user = st.session_state.current_user
    user_id = user["id"]
    
    # Current date formatting
    now_date = datetime.now().strftime("%A, %B %d, %Y")

    # Database connections to pull stats
    conn = get_connection()
    cursor = conn.cursor()
    
    # Study session statistics
    cursor.execute(
        "SELECT SUM(planned_hours), SUM(completed_hours) FROM study_sessions WHERE exam_id IN (SELECT id FROM exams WHERE user_id = ?)",
        (user_id,)
    )
    study_stats = cursor.fetchone()
    planned_hrs = float(study_stats[0] or 0.0)
    completed_hrs = float(study_stats[1] or 0.0)
    progress_percent = int((completed_hrs / planned_hrs * 100)) if planned_hrs > 0 else 0

    # Scheduled Calendar syncs count
    cursor.execute("SELECT COUNT(*) FROM scheduled_sessions WHERE user_id = ?", (user_id,))
    calendar_syncs = cursor.fetchone()[0]
    conn.close()

    assignments = get_assignments(user_id)
    pending_assignments = [a for a in assignments if a["status"] == "Pending"]
    exams = get_exams(user_id)

    # 1. Custom CSS and Header Section
    st.markdown(f"""
    <style>
    .dashboard-header {{
        margin-bottom: 28px;
    }}
    .dashboard-date {{
        font-size: 0.85em;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }}
    .dashboard-greeting {{
        font-size: 2.2em;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -1.2px;
        margin: 0 0 6px 0;
    }}
    .dashboard-summary {{
        color: #475569;
        font-size: 1.05em;
        margin: 0;
    }}
    /* Metrics Flex Grid */
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 16px;
        margin-bottom: 32px;
        width: 100%;
    }}
    @media (max-width: 1024px) {{
        .stats-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}
    @media (max-width: 640px) {{
        .stats-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    .stat-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        position: relative;
        overflow: hidden;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .stat-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }}
    .stat-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
    }}
    .stat-card.blue::before {{ background: #2563EB; }}
    .stat-card.orange::before {{ background: #F59E0B; }}
    .stat-card.green::before {{ background: #10B981; }}
    .stat-card.indigo::before {{ background: #6366F1; }}
    .stat-card.purple::before {{ background: #8B5CF6; }}
    .stat-icon {{
        font-size: 24px;
        margin-bottom: 12px;
    }}
    .stat-value {{
        font-size: 1.85em;
        font-weight: 700;
        color: #0F172A;
        line-height: 1;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }}
    .stat-label {{
        font-size: 0.85em;
        font-weight: 600;
        color: #64748B;
        margin-bottom: 6px;
    }}
    .stat-trend {{
        font-size: 0.75em;
        font-weight: 500;
    }}
    .stat-trend.up {{ color: #10B981; }}
    .stat-trend.down {{ color: #EF4444; }}
    .stat-trend.neutral {{ color: #64748B; }}
    /* Panel Cards */
    .saas-panel-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
    }}
    .saas-panel-title {{
        font-size: 1.15em;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 16px;
        letter-spacing: -0.3px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    /* Today Schedule Item */
    .schedule-item {{
        background-color: #FFFFFF;
        padding: 16px;
        border-left: 4px solid #2563EB;
        border-top: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-radius: 0 12px 12px 0;
        margin-bottom: 12px;
    }}
    .schedule-item.completed {{
        border-left-color: #10B981;
    }}
    /* Deadline Card */
    .saas-deadline-card {{
        background-color: #FFFFFF;
        padding: 16px;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin-bottom: 12px;
    }}
    </style>
    
    <div class="dashboard-header">
        <div class="dashboard-date">{now_date}</div>
        <h2 class="dashboard-greeting">Welcome back, {escaped_name}! 👋</h2>
        <p class="dashboard-summary">Here is your academic overview for today. Keep tracking your milestones!</p>
    </div>
    """, unsafe_allow_html=True)

    # Calculate Trend labels/values dynamically
    task_trend_label = "Tasks completed" if len(pending_assignments) == 0 else f"{len(pending_assignments)} remaining"
    exam_trend_label = f"Next exam pending" if len(exams) > 0 else "All clear"
    hours_trend_label = f"{round(planned_hrs - completed_hrs, 1)} hrs remaining" if planned_hrs > completed_hrs else "Target achieved"
    sync_trend_label = "Connected" if calendar_syncs > 0 else "Not configured"
    rate_trend_label = "On track" if progress_percent >= 50 else "Needs focus"

    # Render custom HTML cards grid
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card orange">
            <span class="stat-icon">📝</span>
            <span class="stat-value">{len(pending_assignments)}</span>
            <span class="stat-label">Pending Tasks</span>
            <span class="stat-trend neutral">{task_trend_label}</span>
        </div>
        <div class="stat-card blue">
            <span class="stat-icon">✏️</span>
            <span class="stat-value">{len(exams)}</span>
            <span class="stat-label">Upcoming Exams</span>
            <span class="stat-trend neutral">{exam_trend_label}</span>
        </div>
        <div class="stat-card green">
            <span class="stat-icon">🕒</span>
            <span class="stat-value">{round(completed_hrs, 1)}h</span>
            <span class="stat-label">Study Hours Done</span>
            <span class="stat-trend up">↑ {hours_trend_label}</span>
        </div>
        <div class="stat-card indigo">
            <span class="stat-icon">📅</span>
            <span class="stat-value">{calendar_syncs}</span>
            <span class="stat-label">Calendar Syncs</span>
            <span class="stat-trend neutral">{sync_trend_label}</span>
        </div>
        <div class="stat-card purple">
            <span class="stat-icon">📈</span>
            <span class="stat-value">{progress_percent}%</span>
            <span class="stat-label">Completion Rate</span>
            <span class="stat-trend rate_trend_label">{rate_trend_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Two column details: Today's study progress and upcoming schedules
    c1, c2 = st.columns([1.1, 0.9], gap="large")

    with c1:
        # Study Progress Panel
        st.markdown("""
        <div class="saas-panel-card">
            <div class="saas-panel-title">📈 Overall Preparation Progress</div>
            <p style="margin: 0 0 16px 0; font-size: 0.9em; color: #64748B;">Completed study hours vs. planned hours across all registered exams.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(min(progress_percent / 100.0, 1.0))
        st.markdown(f"""
        <div style="font-size: 0.85em; color: #475569; margin-top: 8px; font-weight: 500;">
            <b>{progress_percent}% Complete</b> | {round(completed_hrs, 1)} / {round(planned_hrs, 1)} study hours tracked
        </div>
        <br>
        """, unsafe_allow_html=True)

        # Today's study blocks details
        st.markdown("""
        <div class="saas-panel-card" style="margin-top: 10px;">
            <div class="saas-panel-title">🕒 Today's Schedule Overview</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Pull study sessions for today
        conn = get_connection()
        cursor = conn.cursor()
        today_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT * FROM study_sessions WHERE exam_id IN (SELECT id FROM exams WHERE user_id = ?) AND session_date LIKE ? ORDER BY session_date ASC",
            (user_id, f"{today_str}%")
        )
        today_sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not today_sessions:
            st.info("No study sessions scheduled for today. Have a break or add exams in the Exams tab!")
        else:
            for sess in today_sessions:
                status_class = "completed" if sess["status"] == "COMPLETED" else "planned"
                status_color = "#10B981" if sess["status"] == "COMPLETED" else "#2563EB"
                escaped_subject = html.escape(sess['subject'])
                st.markdown(
                    f"""
                    <div class="schedule-item {status_class}" style="border-left-color: {status_color};">
                        <h4 style="margin: 0 0 4px 0; color: #0F172A; font-size: 1.05em; font-weight: 600;">{escaped_subject}</h4>
                        <p style="margin: 0; font-size: 0.85em; color: #475569;">Duration: <b>{sess['planned_hours']} hours</b> | Status: <span style="color: {status_color}; font-weight: 600;">{sess['status']}</span></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with c2:
        st.markdown("""
        <div class="saas-panel-card">
            <div class="saas-panel-title">🚨 Deadline Alerts</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Pull nearest assignments and exams
        st.write("##### Upcoming Assignments")
        if not pending_assignments:
            st.success("All assignments completed!")
        else:
            for item in pending_assignments[:3]:
                priority_color = "#EF4444" if item['priority'] == 'High' else "#F59E0B" if item['priority'] == 'Medium' else "#10B981"
                priority_bg = "#FEF2F2" if item['priority'] == 'High' else "#FFF7ED" if item['priority'] == 'Medium' else "#F0FDF4"
                escaped_title = html.escape(item['title'])
                st.markdown(
                    f"""
                    <div class="saas-deadline-card">
                        <h5 style="margin: 0 0 6px 0; color: #0F172A; font-weight: 600; font-size: 0.95em;">{escaped_title}</h5>
                        <p style="margin: 0 0 6px 0; font-size: 0.85em; color: #475569;">Due Date: <b>{item['due_date']}</b></p>
                        <span style="font-size: 0.75em; font-weight: 700; color: {priority_color}; background-color: {priority_bg}; padding: 3px 8px; border-radius: 6px;">{item['priority']} Priority</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.write("##### Upcoming Exams")
        if not exams:
            st.info("No upcoming exams scheduled.")
        else:
            for exam in exams[:2]:
                escaped_exam_subject = html.escape(exam['subject'])
                st.markdown(
                    f"""
                    <div class="saas-deadline-card">
                        <h5 style="margin: 0 0 6px 0; color: #0F172A; font-weight: 600; font-size: 0.95em;">{escaped_exam_subject}</h5>
                        <p style="margin: 0; font-size: 0.85em; color: #475569;">Exam Date: <b>{exam['exam_date']}</b> | Target Prep: <b>{exam['preparation_hours']} hours</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


