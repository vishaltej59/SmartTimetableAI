import streamlit as st
from app.services.assignment_service import (
    add_assignment,
    get_assignments,
    complete_assignment,
    delete_assignment,
)


def render_assignments():
    st.subheader("Assignment Tracker")

    with st.form("assignment_form"):
        title = st.text_input("Assignment Title")
        due_date = st.date_input("Due Date")
        estimated_hours = st.number_input(
            "Estimated Hours", min_value=0.5, value=1.0, step=0.5
        )
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])

        submitted = st.form_submit_button("Add Assignment")

        if submitted:
            if title.strip():
                add_assignment(
                    st.session_state.current_user["id"], title, str(due_date), priority, estimated_hours
                )
                st.success("Assignment added successfully.")
                st.rerun()
            else:
                st.error("Please enter assignment title.")

    st.divider()

    assignments = get_assignments(st.session_state.current_user["id"])

    if not assignments:
        st.info("No assignments found.")
    else:
        for item in assignments:
            col1, col2, col3 = st.columns([5, 2, 2])

            with col1:
                st.write(f"**{item['title']}**")
                st.caption(
                    f"Due: {item['due_date']} | Priority: {item['priority']} | Status: {item['status']}"
                )

            with col2:
                if item["status"] != "Completed":
                    if st.button("Complete", key=f"complete_{item['id']}"):
                        complete_assignment(item["id"])
                        st.rerun()

            with col3:
                if st.button("Delete", key=f"delete_{item['id']}"):
                    delete_assignment(item["id"])
                    st.rerun()
