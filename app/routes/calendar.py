import streamlit as st
from app.services.calendar_service import get_upcoming_events
from app.services.gemini_service import summarize_events
from app.services.auth_service import GoogleAuthRequiredException


def render_calendar():
    st.subheader("Calendar & AI Assistant")

    st.write("Connecting to Google Calendar...")
    try:
        events = get_upcoming_events(user_id=st.session_state.current_user["id"])
        if not events:
            st.info("No upcoming events found.")
        else:
            event_text = ""
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                summary = event.get("summary", "No Title")
                event_text += f"{start} - {summary}\n"
                st.write(f"📅 **{start}**: {summary}")

            st.divider()
            st.subheader("AI Summary")
            
            # Use session state to cache the summary and avoid hitting the rate limit on every rerun
            summary_key = f"calendar_summary_{st.session_state.current_user['id']}"
            
            if summary_key in st.session_state:
                st.info("💡 Calendar summary loaded from cache.")
                st.write(st.session_state[summary_key])
                if st.button("🔄 Regenerate AI Summary"):
                    del st.session_state[summary_key]
                    st.rerun()
            else:
                if st.button("✨ Generate AI Summary", type="primary"):
                    with st.spinner("Generating summary with Gemini..."):
                        try:
                            summary_text = summarize_events(event_text)
                            st.session_state[summary_key] = summary_text
                            st.rerun()
                        except Exception as e:
                            err_msg = str(e)
                            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                                st.warning("⚠️ **Gemini API Key Rate Limit/Quota Exceeded**\n\nYour API key has hit the free-tier limit. Please wait a minute or replace/upgrade your API key in the `.env` file.")
                            elif "403" in err_msg or "PERMISSION_DENIED" in err_msg:
                                st.error("🚫 **Access Denied (403)**\n\nGoogle has denied access for your API project. Please create a new project in Google AI Studio, generate a new API key, and update your `.env` file.")
                            else:
                                st.error(f"Failed to generate summary: {err_msg}")

    except GoogleAuthRequiredException:
        raise
    except Exception as e:
        st.error(f"Failed to fetch calendar events: {str(e)}")
        st.info(
            "Make sure you have placed credentials.json in the credentials/ directory."
        )
