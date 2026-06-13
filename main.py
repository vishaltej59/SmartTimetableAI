import streamlit as st
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from app.database.db import init_database
from app.routes.dashboard import render_dashboard
from app.routes.assignments import render_assignments
from app.routes.calendar import render_calendar
from app.routes.exams import render_exams
from app.routes.chat import render_chat
from app.routes.study_planner import render_study_planner
from app.routes.study_progress import render_study_progress

# Initialize database
init_database()

st.set_page_config(
    page_title="Smart Timetable AI",
    page_icon="📅",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: transparent;
}
.block-container {
    padding-top: 2rem;
}
.assignment-card {
    background-color: #1e1e1e;
    color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #333333;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    margin-bottom: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.assignment-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.4);
}
.assignment-card h4 {
    margin-top: 0;
    margin-bottom: 8px;
    color: #ffffff !important;
}
.assignment-card p {
    color: #cccccc !important;
    margin: 4px 0;
    font-size: 0.95em;
}
.status-pending {
    color: #ef4444;
    font-weight: 700;
}
.status-completed {
    color: #22c55e;
    font-weight: 700;
}
.priority-high {
    background-color: #ef4444;
    color: white !important;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
    display: inline-block;
}
.priority-medium {
    background-color: #f97316;
    color: white !important;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
    display: inline-block;
}
.priority-low {
    background-color: #22c55e;
    color: white !important;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

st.title("Smart Timetable AI Agent")

# User Account Switcher / Registration in the Sidebar
st.sidebar.subheader("User Account")

# Fetch all users
from app.database.db import get_connection
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

users = get_all_users()

if "current_user" not in st.session_state:
    if users:
        st.session_state.current_user = users[0]
    else:
        st.session_state.current_user = {"id": 1, "email": "localuser@example.com", "name": "Local User"}

user_options = [f"{u['name']} ({u['email']})" for u in users]
current_index = 0
for idx, u in enumerate(users):
    if u["id"] == st.session_state.current_user["id"]:
        current_index = idx
        break

if user_options:
    selected_user_str = st.sidebar.selectbox(
        "Active Profile",
        user_options,
        index=current_index,
        key="active_user_dropdown"
    )
    for u in users:
        if f"{u['name']} ({u['email']})" == selected_user_str:
            if st.session_state.current_user["id"] != u["id"]:
                st.session_state.current_user = u
                st.rerun()
else:
    st.sidebar.warning("No users registered yet.")

# Register New User Form
with st.sidebar.expander("Register New Account"):
    new_name = st.text_input("Full Name", key="register_name")
    new_email = st.text_input("Email Address", key="register_email")
    if st.button("Create Profile"):
        if new_name.strip() and new_email.strip():
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)",
                    (new_name.strip(), new_email.strip())
                )
                conn.commit()
                # Set as current user
                cursor.execute("SELECT * FROM users WHERE email = ?", (new_email.strip(),))
                st.session_state.current_user = dict(cursor.fetchone())
                conn.close()
                st.success("Account created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create account: {e}")
                conn.close()
        else:
            st.warning("Please enter name and email.")

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Assignments", "Exams", "Calendar", "AI Assistant", "Study Planner", "Study Progress"]
)

if page == "Dashboard":
    render_dashboard()
elif page == "Assignments":
    render_assignments()
elif page == "Exams":
    render_exams()
elif page == "Calendar":
    render_calendar()
elif page == "AI Assistant":
    render_chat()
elif page == "Study Planner":
    render_study_planner()
elif page == "Study Progress":
    render_study_progress()
