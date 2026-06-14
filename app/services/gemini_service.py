import os
import time
from google import genai


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)


def summarize_events(events_text: str) -> str:
    client = get_gemini_client()
    prompt = f"""
These are my upcoming calendar events:

{events_text}

Summarize them in simple English.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response.text
    except Exception as e:
        # If gemini-2.5-flash is unavailable or overloaded, instantly fallback to gemini-1.5-flash
        if any(code in str(e) for code in ["503", "429"]):
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash", contents=prompt
                )
                return response.text
            except Exception as fallback_err:
                raise fallback_err
        raise e
