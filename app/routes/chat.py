from app.config import Config
import streamlit as st
import logging
from datetime import datetime, timedelta
import pytz
from app.services.ai_service import send_message_to_groq
from app.services.calendar_service import create_event


def render_chat():
    st.subheader("AI Scheduling Assistant")
    st.write(
        "Ask me to schedule study blocks, find free time, or manage your assignments!"
    )

    # Test Button
    if st.button("Create Test Event"):
        now = datetime.now(pytz.timezone(Config.TIMEZONE))
        tomorrow = now + timedelta(days=1)
        start_dt = tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(minutes=30)
        try:
            logging.info(f"[CREATE EVENT] Attempting to create TEST_EVENT_NOW")
            event = create_event(
                "TEST_EVENT_NOW", start_dt.isoformat(), end_dt.isoformat()
            )
            st.success("Test Event Created Successfully!")
            st.write(f"**Event ID:** {event.get('id')}")
            st.write(f"**Calendar ID:** primary")
            st.write(f"**Start Time:** {start_dt.isoformat()}")
            st.write(f"**End Time:** {end_dt.isoformat()}")
        except Exception as e:
            st.error(f"Failed to create test event: {e}")

    # Initialize chat session in state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    import re

    def clean_ui_message(text):
        if not isinstance(text, str):
            return ""
        # Remove <function=...> tags
        text = re.sub(r"<function=[^>]+>", "", text)
        return text.strip()

    # Display chat history (filtering out system and tool messages for UI clarity)
    for message in st.session_state.messages:
        role = message.get("role")
        if role in ["user", "assistant"] and message.get("content"):
            cleaned = clean_ui_message(message["content"])
            if cleaned:
                with st.chat_message(role):
                    st.markdown(cleaned)

    # Accept user input
    if prompt := st.chat_input("E.g., Schedule 2 hours for DSA tomorrow"):
        # Add user message to state and display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Pass the entire message history to our Groq loop
                    response_text, updated_messages = send_message_to_groq(
                        st.session_state.messages
                    )
                    cleaned_resp = clean_ui_message(response_text)
                    if cleaned_resp:
                        st.markdown(cleaned_resp)
                    # The updated_messages contains the new history, so we sync it
                    st.session_state.messages = updated_messages
                except Exception as e:
                    st.error(f"Error communicating with AI: {e}")
