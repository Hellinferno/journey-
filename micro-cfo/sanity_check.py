import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# We ONLY test the model we know works
model = genai.GenerativeModel("gemini-2.5-flash")

print("Testing Gemini 2.5 Flash...")
try:
    response = model.generate_content("Hello, are you online?")
    print(f"✅ Success! Response: {response.text}")
except Exception as e:
    print(f"❌ Failed: {e}")
