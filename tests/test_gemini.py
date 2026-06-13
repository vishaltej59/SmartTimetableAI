import google.generativeai as genai

import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("Say hello")

print(response.text)

from google import genai

import os
client = genai.Client(

api_key=os.getenv("GEMINI_API_KEY")

)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello"
)

print(response.text)