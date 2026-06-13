import streamlit as st
from app.services.assignment_service import get_assignments


def render_dashboard():
    st.subheader("Dashboard")

    user_id = st.session_state.current_user["id"]
    assignments = get_assignments(user_id)
    pending_count = len([a for a in assignments if a["status"] == "Pending"])
    completed_count = len([a for a in assignments if a["status"] == "Completed"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Assignments", len(assignments))
    col2.metric("Pending", pending_count)
    col3.metric("Completed", completed_count)

    st.divider()
    st.subheader("Upcoming Work")

    if not assignments:
        st.info("No assignments added yet.")
    else:
        for item in assignments[:5]:
            st.markdown(
                f"""
                <div class="assignment-card">
                    <h4>{item['title']}</h4>
                    <p>Due: {item['due_date']}</p>
                    <p>Priority: <span class="priority-{item['priority'].lower()}">{item['priority']}</span></p>
                    <p>Status: <span class="status-{item['status'].lower()}">{item['status']}</span></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
