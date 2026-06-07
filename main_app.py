import streamlit as st
from database import init_database
from services.assignment_service import (
    add_assignment,
    get_assignments,
    complete_assignment,
    delete_assignment
)

init_database()

st.set_page_config(
    page_title="Smart Timetable Assistant",
    page_icon="📅",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #f6f8fb;
}
.block-container {
    padding-top: 2rem;
}
.assignment-card {
    background: white;
    padding: 18px;
    border-radius: 10px;
    border-left: 6px solid #4f46e5;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}
.status-pending {
    color: #dc2626;
    font-weight: 700;
}
.status-completed {
    color: #16a34a;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

st.title("Smart Timetable Assistant")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Assignments", "Calendar", "AI Assistant"]
)

assignments = get_assignments()
pending_count = len([a for a in assignments if a["status"] == "Pending"])
completed_count = len([a for a in assignments if a["status"] == "Completed"])

if page == "Dashboard":
    st.subheader("Dashboard")

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
                    <p>Priority: {item['priority']}</p>
                    <p>Status: <span class="status-{item['status'].lower()}">{item['status']}</span></p>
                </div>
                """,
                unsafe_allow_html=True
            )

elif page == "Assignments":
    st.subheader("Assignment Tracker")

    with st.form("assignment_form"):
        title = st.text_input("Assignment Title")
        due_date = st.date_input("Due Date")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])

        submitted = st.form_submit_button("Add Assignment")

        if submitted:
            if title.strip():
                add_assignment(title, str(due_date), priority)
                st.success("Assignment added successfully.")
                st.rerun()
            else:
                st.error("Please enter assignment title.")

    st.divider()

    assignments = get_assignments()

    if not assignments:
        st.info("No assignments found.")
    else:
        for item in assignments:
            col1, col2, col3 = st.columns([5, 2, 2])

            with col1:
                st.write(f"**{item['title']}**")
                st.caption(f"Due: {item['due_date']} | Priority: {item['priority']} | Status: {item['status']}")

            with col2:
                if item["status"] != "Completed":
                    if st.button("Complete", key=f"complete_{item['id']}"):
                        complete_assignment(item["id"])
                        st.rerun()

            with col3:
                if st.button("Delete", key=f"delete_{item['id']}"):
                    delete_assignment(item["id"])
                    st.rerun()

elif page == "Calendar":
    st.subheader("Calendar")
    st.info("Day 2: Connect Google Calendar events here.")

elif page == "AI Assistant":
    st.subheader("AI Assistant")
    st.info("Day 3: Add Gemini summary/chat here.")