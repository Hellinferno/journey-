import google.generativeai as genai
import os
import json
import re
from app.schemas import InvoiceData
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# 1. Configure API
if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def clean_json_text(text: str) -> str:
    """Robustly extracts JSON object from AI response."""
    # Remove markdown code blocks like ```json ... ```
    text = re.sub(r"```(json)?", "", text).replace("```", "").strip()
    
    # 2. Find the actual JSON object (start at first '{', end at last '}')
    start = text.find("{")
    end = text.rfind("}")
    
    if start != -1 and end != -1:
        return text[start:end+1]
    return text

def analyze_invoice(image_path: str) -> InvoiceData:
    """
    Sends image to Gemini 2.5 Flash (current stable version).
    """
    # 3. Use ONLY the single working model
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.1
        }
    )

    try:
        with Image.open(image_path) as img:
            prompt = """
            Extract data from this Indian invoice in strict JSON:
            {
                "vendor_name": "string",
                "invoice_number": "string or null",
                "date": "YYYY-MM-DD or null",
                "total_amount": float,
                "tax_amount": float,
                "gstin": "string or null",
                "currency": "string"
            }
            """
            
            print("📤 Sending to Gemini 2.5 Flash...")
            response = model.generate_content([prompt, img])
            
            # 4. Clean and Parse
            clean_text = clean_json_text(response.text)
            print(f"📥 Parsed: {clean_text}")

            json_data = json.loads(clean_text)
            return InvoiceData(**json_data)

    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        raise e
