import os
from google import genai
from dotenv import load_dotenv

load_dotenv("_git 2/.env")

def test_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        return
        
    client = genai.Client(api_key=api_key)
    models = [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-pro-latest",
        "gemini-2.5-pro"
    ]
    
    print(f"Testing Gemini models using API key: {api_key[:10]}...{api_key[-5:]}\n")
    
    print("Writing available models to scratch/available_models.txt...")
    try:
        with open("scratch/available_models.txt", "w") as f_out:
            for m in client.models.list():
                f_out.write(f"Model: {m.name}\n")
        print("Success writing model list.")
    except Exception as e:
        print(f"Failed to list models: {e}\n")
        
    for model in models:
        print(f"\n--- Testing {model} ---")
        try:
            response = client.models.generate_content(
                model=model,
                contents="Say hello"
            )
            print(f"SUCCESS: {response.text.strip()}")
        except Exception as e:
            print(f"FAILED: {e}\n")

if __name__ == '__main__':
    test_models()
