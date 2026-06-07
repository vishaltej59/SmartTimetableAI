from google import genai

client = genai.Client(
    api_key="AQ.Ab8RN6K1KJ1JPMW2erAZns_h4v6OFh3sMpsI5cjjDM8IuhXz2w"
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello"
)

print(response.text)