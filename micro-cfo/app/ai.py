import google.generativeai as genai
import os
import json
import re
from app.schemas import InvoiceData
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Configure API
if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def clean_json_text(text: str) -> str:
    """Robustly extracts JSON object from AI response."""
    # 1. Strip markdown code blocks
    text = re.sub(r"```(json)?", "", text).replace("```", "").strip()
    
    # 2. Find the actual JSON object (start at first '{', end at last '}')
    start = text.find("{")
    end = text.rfind("}")
    
    if start != -1 and end != -1:
        return text[start:end+1]
    return text

def analyze_invoice(image_path: str) -> InvoiceData:
    """
    Sends image to Gemini 1.5 Flash.
    """
    # Use the single best model for speed & accuracy
    # Note: We append multiple candidates to a list to handle 404 access issues
    model_names = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro-vision"]
    
    last_error = None
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.1
                }
            )

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
                
                print(f"📤 Sending to Gemini ({model_name})...")
                response = model.generate_content([prompt, img])
                
                # Robust Parsing
                clean_text = clean_json_text(response.text)
                print(f"📥 Parsed JSON: {clean_text}")

                json_data = json.loads(clean_text)
                return InvoiceData(**json_data)
        except Exception as e:
            print(f"❌ Model {model_name} Error: {e}")
            last_error = e
            
    # If vision fails, the user would prefer to know why
    raise last_error
