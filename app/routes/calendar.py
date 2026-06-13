import streamlit as st
from app.services.calendar_service import get_upcoming_events
from app.services.gemini_service import summarize_events


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
            with st.spinner("Generating summary with Gemini..."):
                try:
                    summary_text = summarize_events(event_text)
                    st.write(summary_text)
                except Exception as e:
                    st.error(f"Failed to generate summary: {str(e)}")

    except Exception as e:
        st.error(f"Failed to fetch calendar events: {str(e)}")
        st.info(
            "Make sure you have placed credentials.json in the credentials/ directory."
        )
