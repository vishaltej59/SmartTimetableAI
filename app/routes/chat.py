from app.config import Config
import streamlit as st
import logging
from datetime import datetime, timedelta
import pytz
from app.services.ai_service import send_message_to_groq
from app.services.calendar_service import create_event
from app.services.auth_service import GoogleAuthRequiredException
import re

def render_chat():
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-size: 2em; font-weight: 800; color: #0F172A; letter-spacing: -1px; margin-bottom: 4px;">AI Study Assistant</h2>
        <p style="color: #475569; font-size: 1.05em; margin: 0;">Collaborate with the AI to organize your study schedule, manage classes, and maximize productivity.</p>
    </div>
    """, unsafe_allow_html=True)

    # Injected CSS for chat styling
    st.markdown("""
    <style>
    /* Chat Message Styles */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    }
    [data-testid="stChatMessageContent"] p {
        font-size: 0.95em !important;
        line-height: 1.6 !important;
        color: #1E293B !important;
    }
    /* Suggestions pills hover styles */
    div.stButton > button {
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover {
        border-color: #2563EB !important;
        color: #2563EB !important;
        background-color: #EFF6FF !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Developer Controls Expander
    with st.expander("🛠️ Developer / Testing Controls"):
        if st.button("Create Test Event", use_container_width=True):
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
            except GoogleAuthRequiredException:
                raise
            except Exception as e:
                st.error(f"Failed to create test event: {e}")

    # Initialize chat session in state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    def clean_ui_message(text):
        if not isinstance(text, str):
            return ""
        # Remove <function=...> tags
        text = re.sub(r"<function=[^>]+>", "", text)
        return text.strip()

    # Display chat history (filtering out system and tool messages for UI clarity)
    if st.session_state.messages:
        for message in st.session_state.messages:
            role = message.get("role")
            if role in ["user", "assistant"] and message.get("content"):
                cleaned = clean_ui_message(message["content"])
                if cleaned:
                    with st.chat_message(role):
                        st.markdown(cleaned)

    # Empty State & Suggestion Pills
    quick_prompt = None
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; margin: 40px 0 24px 0;">
            <span style="font-size: 44px;">🤖</span>
            <h3 style="font-weight: 700; color: #0F172A; margin-top: 16px; margin-bottom: 8px; font-size: 1.45em; letter-spacing: -0.5px;">Meet your AI study planner</h3>
            <p style="color: #64748B; font-size: 0.95em; max-width: 480px; margin: 0 auto;">Ask me to construct study plans, sync calendars, organize assignment tasks, or get prep tips.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📅 Generate a personalized study plan", use_container_width=True):
                quick_prompt = "Generate a personalized study plan for my exams"
            if st.button("🔍 Find free slots in my calendar", use_container_width=True):
                quick_prompt = "Find free slots in my calendar this week"
        with c2:
            if st.button("🗓️ Schedule my study week", use_container_width=True):
                quick_prompt = "Schedule my study blocks for the upcoming week"
            if st.button("📝 Help me prepare for my exams", use_container_width=True):
                quick_prompt = "Help me prepare a strategy for my registered exams"
    else:
        # Suggestion suggestions row above input
        st.write("")
        st.markdown("<p style='font-size:0.85em; font-weight:600; color:#64748B; margin-bottom:8px;'>💡 Quick prompts:</p>", unsafe_allow_html=True)
        cols = st.columns(4)
        with cols[0]:
            if st.button("📅 Plan Exams", key="qp_exams", use_container_width=True):
                quick_prompt = "Generate study plan for my exams"
        with cols[1]:
            if st.button("🗓️ Schedule Week", key="qp_week", use_container_width=True):
                quick_prompt = "Schedule my week"
        with cols[2]:
            if st.button("🔍 Free Slots", key="qp_slots", use_container_width=True):
                quick_prompt = "Find free slots"
        with cols[3]:
            if st.button("✏️ Prep Tips", key="qp_prep", use_container_width=True):
                quick_prompt = "Prepare for exams"

    # Accept user input
    user_input = st.chat_input("E.g., Schedule 2 hours for DSA tomorrow")
    if quick_prompt:
        user_input = quick_prompt

    if user_input:
        # Add user message to state and display
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display immediately (since st.chat_input triggers rerun, we append then run Groq)
        # Note: Groq is called in user context, response appended to state
        try:
            # Append Groq response to history
            with st.spinner("Thinking..."):
                response_text, updated_messages = send_message_to_groq(
                    st.session_state.messages
                )
            st.session_state.messages = updated_messages
            st.rerun()
        except GoogleAuthRequiredException:
            raise
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                st.warning("⚠️ **Gemini API Key Rate Limit/Quota Exceeded**\n\nYour API key has hit the free-tier limit. Please wait a minute or replace/upgrade your API key in the `.env` file.")
            elif "403" in err_msg or "PERMISSION_DENIED" in err_msg:
                st.error("🚫 **Access Denied (403)**\n\nGoogle has denied access for your API project. Please create a new project in Google AI Studio, generate a new API key, and update your `.env` file.")
            else:
                st.error(f"Error communicating with AI: {err_msg}")

