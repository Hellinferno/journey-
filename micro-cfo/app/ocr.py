import google.generativeai as genai
import os
import json
from PIL import Image
from app.schemas import InvoiceData

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def analyze_invoice(image_path: str) -> InvoiceData:
    """
    Sends image to Gemini 1.5 Flash and returns structured InvoiceData.
    """
    
    # 1. Setup Model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )

    # 2. Prompt Engineering
    prompt = """
    Analyze this Indian invoice image. Extract the following fields in JSON:
    - vendor_name (string)
    - invoice_number (string or null)
    - date (YYYY-MM-DD or null)
    - total_amount (float)
    - tax_amount (float, defaults to 0)
    - gstin (string or null)
    - currency (string, defaults to INR)
    
    If the text is in Hindi, translate relevant fields to English.
    Ensure total_amount is purely numeric.
    """

    try:
        # 3. Process Image
        img = Image.open(image_path)
        response = model.generate_content([prompt, img])
        
        # 4. Parse & Validate
        json_data = json.loads(response.text)
        return InvoiceData(**json_data)
        
    except Exception as e:
        print(f"OCR Failed: {e}")
        return None
