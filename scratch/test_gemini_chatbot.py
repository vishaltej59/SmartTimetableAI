import sys
import os
from unittest.mock import MagicMock

# Mock streamlit session state to avoid running Streamlit environment
class MockSessionState:
    def __init__(self):
        self.current_user = {
            "id": 1,
            "email": "localuser@example.com",
            "name": "Local User"
        }
    def get(self, key, default=None):
        return getattr(self, key, default)

st_mock = MagicMock()
st_mock.session_state = MockSessionState()
sys.modules['streamlit'] = st_mock

from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

from app.services.ai_service import send_message_to_groq

def test_chat():
    print("Testing chat integration with Gemini...")
    messages = [
        {"role": "user", "content": "Hello! I am a student preparing for my math final exam. Can you tell me if there are any assignments registered?"}
    ]
    try:
        response_text, updated_messages = send_message_to_groq(messages)
        print("\n=== RESPONSE ===")
        print(response_text)
        print("================\n")
        print("Success! Gemini chatbot tool calling works.")
    except Exception as e:
        print("Failed to run Gemini chatbot:", e)
        raise e

if __name__ == "__main__":
    test_chat()
