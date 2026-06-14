import streamlit as st
from app.config import Config
import os

def render_settings():
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-size: 2em; font-weight: 800; color: #0F172A; letter-spacing: -1px; margin-bottom: 4px;">Account & Settings</h2>
        <p style="color: #475569; font-size: 1.05em; margin: 0;">Manage your profile settings, system integration parameters, and calendar connections.</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Profile Details
    st.write("### 👤 Student Profile")
    st.markdown(
        f"""
        <div style="background-color: #ffffff; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <p style="margin: 0 0 8px 0; color: #64748b;">Full Name</p>
            <h4 style="margin: 0 0 16px 0; color: #1e293b;">{st.session_state.current_user['name']}</h4>
            <p style="margin: 0 0 8px 0; color: #64748b;">Email Address</p>
            <h4 style="margin: 0; color: #1e293b;">{st.session_state.current_user['email']}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. System Settings
    st.write("### ⚙️ System Parameters")
    st.markdown(
        f"""
        <div style="background-color: #ffffff; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <p style="margin: 0 0 8px 0; color: #64748b;">Primary Timezone</p>
            <h4 style="margin: 0 0 16px 0; color: #1e293b;">{Config.TIMEZONE}</h4>
            <p style="margin: 0 0 8px 0; color: #64748b;">Database Path</p>
            <h4 style="margin: 0; color: #1e293b;">{Config.DB_PATH}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Integrations status
    st.write("### 🔌 Google Integration")
    user_id = st.session_state.current_user["id"]
    token_path = f"credentials/token_{user_id}.json"
    is_connected = os.path.exists(token_path)

    if is_connected:
        st.success("🟢 Google Calendar is Connected and Active")
        if st.button("Disconnect Google Calendar Session", type="primary"):
            try:
                os.remove(token_path)
                st.success("Session disconnected successfully! Please reload the page.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to disconnect session: {e}")
    else:
        st.warning("🔴 Google Calendar is not connected.")
        st.info("Navigate to the Calendar or Timetable sections to initiate the Google OAuth flow.")
