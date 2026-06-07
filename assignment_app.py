import streamlit as st

st.title("Assignment Tracker")

title = st.text_input("Assignment Name")
due = st.date_input("Due Date")

if st.button("Add Assignment"):
    st.success(f"{title} added successfully!")