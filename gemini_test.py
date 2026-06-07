import google.generativeai as genai

genai.configure(api_key="AQ.Ab8RN6K1KJ1JPMW2erAZns_h4v6OFh3sMpsI5cjjDM8IuhXz2w")

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("Say hello")

print(response.text)