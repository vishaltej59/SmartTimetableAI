from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        exit(1)

    client = genai.Client(api_key=api_key)

    print("Testing with gemini-2.5-flash...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say hello"
        )
        print("Success (gemini-2.5-flash):", response.text)
    except Exception as e:
        print(f"gemini-2.5-flash failed: {e}")
        print("Instantly falling back to gemini-1.5-flash...")
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents="Say hello"
            )
            print("Success (gemini-1.5-flash fallback):", response.text)
        except Exception as fallback_err:
            print("Fallback failed:", fallback_err)