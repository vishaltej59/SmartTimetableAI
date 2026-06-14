import streamlit as st
from app.services.exam_service import add_exam, get_exams, delete_exam
from app.services.study_progress_service import get_exam_readiness
from datetime import datetime
import html

def render_exams():
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-size: 2em; font-weight: 800; color: #0F172A; letter-spacing: -1px; margin-bottom: 4px;">Exams & Readiness</h2>
        <p style="color: #475569; font-size: 1.05em; margin: 0;">Track upcoming exams, monitor study progress, and calculate your academic readiness score.</p>
    </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.current_user["id"]

    # Expandable "Register New Exam" drawer
    with st.expander("➕ Register New Exam"):
        with st.form("exam_form"):
            subject = st.text_input("Subject", placeholder="e.g. Organic Chemistry Final")
            exam_date = st.date_input("Exam Date", datetime.now().date())
            prep_hours = st.number_input(
                "Preparation Hours Needed", min_value=1.0, value=5.0, step=0.5
            )
            syllabus = st.text_area("Syllabus / Topics", placeholder="List of chapters, reference books...")

            submitted = st.form_submit_button("Register Exam", type="primary")

            if submitted:
                if subject.strip():
                    add_exam(
                        user_id, subject, str(exam_date), syllabus, prep_hours
                    )
                    st.success("Exam registered successfully.")
                    st.rerun()
                else:
                    st.error("Please enter a subject.")

    st.write("")

    # Card custom style
    st.markdown("""
    <style>
    .exam-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .exam-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
    }
    .exam-title-group {
        display: flex;
        flex-direction: column;
    }
    .exam-subject {
        font-size: 1.15em;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }
    .exam-date-meta {
        font-size: 0.85em;
        color: #64748B;
        margin-top: 2px;
    }
    .exam-badge {
        font-size: 0.75em;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        white-space: nowrap;
    }
    .badge-urgent { background: #FEF2F2; color: #EF4444; }
    .badge-upcoming { background: #E0F2FE; color: #0284C7; }
    .badge-far { background: #F1F5F9; color: #475569; }
    .badge-today { background: #FFF7ED; color: #EA580C; }
    .badge-passed { background: #F4F4F5; color: #71717A; }
    .progress-section {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-top: 4px;
    }
    .progress-label-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.82em;
        font-weight: 600;
        color: #475569;
    }
    .progress-bar-container {
        background: #E2E8F0;
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
        width: 100%;
        margin: 2px 0;
    }
    .progress-bar-fill {
        background: #2563EB;
        height: 100%;
        border-radius: 6px;
    }
    .exam-syllabus-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 0.85em;
        color: #475569;
        margin-top: 4px;
    }
    .exam-readiness-badge {
        font-size: 0.75em;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
    }
    .readiness-high { background: #E6FBF3; color: #10B981; }
    .readiness-medium { background: #FFF7ED; color: #F97316; }
    .readiness-low { background: #FEF2F2; color: #EF4444; }
    </style>
    """, unsafe_allow_html=True)

    exams = get_exams(user_id)

    if not exams:
        st.info("No registered exams found. Use the form above to add your first exam!")
    else:
        for item in exams:
            # Calculate days remaining
            badge_class = "badge-far"
            badge_text = "Upcoming"
            
            try:
                exam_dt = datetime.strptime(item['exam_date'], "%Y-%m-%d").date()
                today = datetime.now().date()
                days_left = (exam_dt - today).days
                
                if days_left < 0:
                    badge_class = "badge-passed"
                    badge_text = "Passed"
                elif days_left == 0:
                    badge_class = "badge-today"
                    badge_text = "TODAY"
                elif days_left == 1:
                    badge_class = "badge-urgent"
                    badge_text = "1 day remaining"
                elif days_left <= 3:
                    badge_class = "badge-urgent"
                    badge_text = f"{days_left} days remaining"
                elif days_left <= 7:
                    badge_class = "badge-upcoming"
                    badge_text = f"{days_left} days remaining"
                else:
                    badge_class = "badge-far"
                    badge_text = f"{days_left} days remaining"
            except Exception:
                badge_text = "Date TBD"
            
            # Calculate readiness
            readiness_data = get_exam_readiness(item['id'], item['preparation_hours'])
            total_completed = readiness_data["total_completed"]
            readiness_score = readiness_data["readiness_score"]
            
            # Progress bar width percentage
            req_hours = float(item['preparation_hours'])
            pct = min(int((total_completed / req_hours) * 100), 100) if req_hours > 0 else 0
            
            if readiness_score >= 80:
                readiness_class = "readiness-high"
            elif readiness_score >= 40:
                readiness_class = "readiness-medium"
            else:
                readiness_class = "readiness-low"

            escaped_subject = html.escape(item["subject"])
            escaped_syllabus = html.escape(item["syllabus"]) if item["syllabus"] else ""

            syllabus_html = ""
            if escaped_syllabus:
                syllabus_html = f'<div class="exam-syllabus-box" style="white-space: pre-wrap;"><b>Syllabus:</b> {escaped_syllabus}</div>'

            st.markdown(f'<div class="exam-card">'
                        f'<div class="exam-header">'
                        f'<div class="exam-title-group">'
                        f'<h4 class="exam-subject">{escaped_subject}</h4>'
                        f'<div class="exam-date-meta"><span>Exam Date: <b>{item["exam_date"]}</b></span></div>'
                        f'</div>'
                        f'<span class="exam-badge {badge_class}">{badge_text}</span>'
                        f'</div>'
                        f'<div class="progress-section">'
                        f'<div class="progress-label-row">'
                        f'<span>Study Progress: {round(total_completed, 1)}h done / {item["preparation_hours"]}h required</span>'
                        f'<span class="exam-readiness-badge {readiness_class}">Readiness: {readiness_score}%</span>'
                        f'</div>'
                        f'<div class="progress-bar-container"><div class="progress-bar-fill" style="width: {pct}%;"></div></div>'
                        f'</div>'
                        f'{syllabus_html}'
                        f'</div>', unsafe_allow_html=True)

            col_delete, col_spacer = st.columns([1, 4])
            with col_delete:
                if st.button("Delete Exam", key=f"delete_exam_{item['id']}", use_container_width=True):
                    delete_exam(item["id"])
                    st.success("Exam deleted.")
                    st.rerun()
            st.write("")

