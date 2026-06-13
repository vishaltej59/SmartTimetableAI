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
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return response.text
        except Exception as e:
            # Retry if we hit a 503 or 429 error and we haven't exhausted our retries
            if (
                any(code in str(e) for code in ["503", "429"])
                and attempt < max_retries - 1
            ):
                time.sleep(2**attempt)  # 1s, 2s backoff
                continue
            raise
