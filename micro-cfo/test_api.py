
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


try:
    with open("working_models.txt", "r", encoding="utf-16") as f:
        models = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"Error reading working_models.txt: {e}")
    models = ["models/gemini-1.5-flash", "models/gemini-pro"]


import PIL.Image

# Test image generation on specific Working model
target_model = "models/gemini-3-pro-preview-12-2025"
print(f"Testing IMAGE generation with {target_model}...")

try:
    img = PIL.Image.open("temp_invoice.jpg")
    model = genai.GenerativeModel(target_model)
    response = model.generate_content(["Describe this image", img])
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Failed with image: {e}")

