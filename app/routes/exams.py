import streamlit as st
from app.services.exam_service import add_exam, get_exams, delete_exam


def render_exams():
    st.subheader("Exam Management")

    with st.form("exam_form"):
        subject = st.text_input("Subject")
        exam_date = st.date_input("Exam Date")
        prep_hours = st.number_input(
            "Preparation Hours Needed", min_value=1.0, value=5.0, step=0.5
        )
        syllabus = st.text_area("Syllabus / Topics")

        submitted = st.form_submit_button("Add Exam")

        if submitted:
            if subject.strip():
                add_exam(
                    st.session_state.current_user["id"], subject, str(exam_date), syllabus, prep_hours
                )
                st.success("Exam added successfully.")
                st.rerun()
            else:
                st.error("Please enter a subject.")

    st.divider()

    exams = get_exams(st.session_state.current_user["id"])

    if not exams:
        st.info("No exams found.")
    else:
        for item in exams:
            col1, col2 = st.columns([8, 2])

            with col1:
                st.write(f"**{item['subject']}**")
                st.caption(
                    f"Date: {item['exam_date']} | Prep: {item['preparation_hours']} hours"
                )
                if item["syllabus"]:
                    st.caption(f"Syllabus: {item['syllabus']}")

            with col2:
                if st.button("Delete", key=f"delete_exam_{item['id']}"):
                    delete_exam(item["id"])
                    st.rerun()
