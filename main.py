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
from app.routes.login import render_login
from app.services.auth_service import GoogleAuthRequiredException, get_google_flow
import os

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

# Process Google OAuth callback redirection
query_params = st.query_params
if "code" in query_params and "state" in query_params:
    code = query_params["code"]
    user_id_str = query_params["state"]
    try:
        from app.database.db import get_connection
        # Retrieve user from DB to authenticate them back if session was lost
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id_str,))
        row = cursor.fetchone()
        conn.close()

        if row:
            user = dict(row)
            
            # Fetch token and save credentials
            flow = get_google_flow(user_id_str)
            flow.code_verifier = "smart_timetable_ai_agent_secret_code_verifier_value_for_pkce_auth_flow_123456789"
            flow.fetch_token(code=code)
            creds = flow.credentials

            # Save credentials for this specific user
            token_path = f"credentials/token_{user_id_str}.json"
            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            with open(token_path, "w") as token:
                token.write(creds.to_json())

            # Log user in
            st.session_state.current_user = user
            st.success("Successfully connected to Google Calendar!")
            st.query_params.clear()
            st.rerun()
        else:
            st.error("OAuth callback: User ID from state parameter not found in database.")
    except Exception as e:
        st.error(f"Failed to authorize Google Calendar: {e}")

# Check if user is authenticated
if "current_user" not in st.session_state:
    render_login()
else:
    st.title("Smart Timetable AI Agent")

    # User Account Info and Logout in the Sidebar
    st.sidebar.subheader("User Account")
    st.sidebar.markdown(f"👤 **{st.session_state.current_user['name']}**")
    st.sidebar.caption(st.session_state.current_user['email'])

    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.pop("current_user", None)
        st.rerun()

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Assignments", "Exams", "Calendar", "AI Assistant", "Study Planner", "Study Progress"]
    )

    try:
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
    except GoogleAuthRequiredException as auth_err:
        st.warning("📅 **Google Calendar Connection Required**")
        st.info("To use this feature, you need to connect your Google Calendar account so the app can sync and schedule your study sessions.")
        st.link_button("🔌 Connect Google Calendar", auth_err.authorization_url, type="primary")
