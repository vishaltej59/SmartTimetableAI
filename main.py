import os
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
import streamlit as st
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from app.database.db import init_database
from app.services.auth_service import GoogleAuthRequiredException, get_google_flow
import os

# Initialize database (cached to execute only once per server start)
@st.cache_resource
def cached_init_db():
    init_database()

cached_init_db()

st.set_page_config(
    page_title="Smart Timetable AI",
    page_icon="📅",
    layout="wide"
)

st.markdown("""<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"><style>
[data-testid="stAppViewContainer"] {
    background-color: #F8FAFC !important;
}
body {
    font-family: 'Inter', sans-serif !important;
    color: #0F172A;
}
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}
.user-profile-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    margin-top: 20px;
    margin-bottom: 10px;
}
.user-profile-card .avatar {
    font-size: 14px;
    font-weight: 600;
    background: #EFF6FF;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    color: #2563EB !important;
    border: 1px solid #BFDBFE;
}
.user-profile-card .profile-info {
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.user-profile-card .name {
    font-weight: 600;
    color: #0F172A;
    font-size: 0.85em;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}
.user-profile-card .email {
    color: #64748B;
    font-size: 0.75em;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}
div[data-testid="stSidebarUserContent"] div[role="radiogroup"] {
    gap: 4px !important;
}
div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    transition: all 0.15s ease !important;
    margin-bottom: 2px !important;
    width: 100% !important;
    cursor: pointer !important;
}
div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label:hover {
    background: #F1F5F9 !important;
    color: #0F172A !important;
}
div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label[data-checked="true"] {
    background: #EFF6FF !important;
    border-color: #BFDBFE !important;
}
div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label div[role="presentation"] {
    display: none !important;
}
div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
    font-weight: 500 !important;
    color: #475569 !important;
    font-size: 0.9em !important;
    margin: 0 !important;
}
div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label[data-checked="true"] div[data-testid="stMarkdownContainer"] p {
    color: #2563EB !important;
    font-weight: 600 !important;
}
div[data-testid="stSidebar"] button {
    background: transparent !important;
    border: 1px solid #E2E8F0 !important;
    color: #EF4444 !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    font-size: 0.85em !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
    font-weight: 500 !important;
}
div[data-testid="stSidebar"] button:hover {
    background: #FEF2F2 !important;
    border-color: #FCA5A5 !important;
    color: #EF4444 !important;
}
.main {
    background-color: transparent;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
    max-width: 1200px;
}
.saas-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    margin-bottom: 24px;
}
</style>""", unsafe_allow_html=True)

# Process Google OAuth callback redirection
query_params = st.query_params
if "code" in query_params and "state" in query_params:
    code = query_params["code"]
    user_id_str = query_params["state"]
    try:
        from app.database.db import get_connection
        
        # Check if Google login from the auth page is active
        if user_id_str == "login":
            flow = get_google_flow("login")
            flow.code_verifier = "smart_timetable_ai_agent_secret_code_verifier_value_for_pkce_auth_flow_123456789"
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # Fetch user email and name using Google API
            # pyrefly: ignore [missing-import]
            from googleapiclient.discovery import build
            service = build('oauth2', 'v2', credentials=creds)
            user_info = service.userinfo().get().execute()
            email = user_info.get("email").strip().lower()
            name = user_info.get("name", "Google User")
            
            # Retrieve or automatically create user
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
                conn.commit()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()
            user = dict(row)
            conn.close()
            
            # Save Google token for this specific user
            token_path = f"credentials/token_{user['id']}.json"
            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
                
            st.session_state.current_user = user
            st.success("Successfully logged in with Google!")
            st.query_params.clear()
            st.rerun()
            
        else:
            # Standard calendar linkage callback flow
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
    from app.routes.login import render_login
    render_login()
else:
    # Sidebar Logo and Navigation list
    st.sidebar.markdown("""
    <div style="padding: 10px 0 20px 0; display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 24px;">📅</span>
        <span style="font-size: 1.15em; font-weight: 700; color: #0F172A; letter-spacing: -0.5px;">Smart Timetable AI</span>
    </div>
    """, unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard", 
            "💬 AI Assistant",
            "📈 Study Progress",
            "🕒 Timetable", 
            "📅 Calendar", 
            "📝 Assignments", 
            "✏️ Exams", 
            "🔔 Reminders", 
            "📁 Data", 
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    # Strip emoji prefix for page route checks
    page_name = page.split(" ", 1)[1] if " " in page else page

    # User Profile card at the bottom of the sidebar
    user_name = st.session_state.current_user['name'] or "Student"
    user_email = st.session_state.current_user['email'] or ""
    avatar_initials = "".join([p[0].upper() for p in user_name.split() if p])[:2] if user_name else "👤"

    st.sidebar.markdown(f"""
    <div class="user-profile-card">
        <div class="avatar">{avatar_initials}</div>
        <div class="profile-info">
            <div class="name">{user_name}</div>
            <div class="email">{user_email}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.pop("current_user", None)
        st.rerun()

    try:
        if page_name == "Dashboard":
            from app.routes.dashboard import render_dashboard
            render_dashboard()
        elif page_name == "AI Assistant":
            from app.routes.chat import render_chat
            render_chat()
        elif page_name == "Study Progress":
            from app.routes.study_progress import render_study_progress
            render_study_progress()
        elif page_name == "Timetable":
            from app.routes.study_planner import render_study_planner
            render_study_planner()
        elif page_name == "Calendar":
            from app.routes.calendar import render_calendar
            render_calendar()
        elif page_name == "Assignments":
            from app.routes.assignments import render_assignments
            render_assignments()
        elif page_name == "Exams":
            from app.routes.exams import render_exams
            render_exams()
        elif page_name == "Reminders":
            from app.routes.reminders import render_reminders
            render_reminders()
        elif page_name == "Data":
            from app.routes.db_viewer import render_db_viewer
            render_db_viewer()
        elif page_name == "Settings":
            from app.routes.settings import render_settings
            render_settings()
    except GoogleAuthRequiredException as auth_err:
        st.warning("📅 **Google Calendar Connection Required**")
        st.info("To use this feature, you need to connect your Google Calendar account so the app can sync and schedule your study sessions.")
        st.link_button("🔌 Connect Google Calendar", auth_err.authorization_url, type="primary")

