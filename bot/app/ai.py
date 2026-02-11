"""
AI Invoice Analyzer
Uses Google Gemini to extract invoice data from images
"""
from google import genai
from google.genai import types
import os
import json
import re
from app.schemas import InvoiceData
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
client = None
if os.getenv("GOOGLE_API_KEY"):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def clean_json_text(text: str) -> str:
    """Extract JSON object from AI response"""
    # Remove markdown code blocks
    text = re.sub(r"```(json)?", "", text).replace("```", "").strip()
    
    # Find JSON object boundaries
    start = text.find("{")
    end = text.rfind("}")
    
    if start != -1 and end != -1:
        return text[start:end+1]
    return text


def analyze_invoice(image_path: str) -> InvoiceData:
    """
    Analyze invoice image using Gemini 2.5 Flash
    
    Args:
        image_path: Path to invoice image file
        
    Returns:
        InvoiceData object with extracted information
    """
    if not client:
        raise ValueError("Google API key not configured")

    try:
        with Image.open(image_path) as img:
            # Convert PIL Image to bytes
            import io
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format=img.format or 'PNG')
            img_bytes = img_byte_arr.getvalue()
            
            prompt = """
            Extract data from this Indian invoice in strict JSON format.
            Analyze the items to determine the appropriate category.
            
            Categories: [Office Supplies, Travel, Food & Beverage, Electronics, 
                        Professional Fees, Utilities, Rent, Other]
            
            CRITICAL:
            - If items are food/drinks, set category to "Food & Beverage"
            - If items are laptops/phones, set category to "Electronics"
            
            JSON Structure:
            {
                "vendor_name": "string",
                "invoice_number": "string or null",
                "date": "YYYY-MM-DD or null",
                "total_amount": float,
                "tax_amount": float,
                "gstin": "string or null",
                "currency": "string",
                "category": "string",
                "item_description": "short summary string"
            }
            """
            
            print("📤 Sending to Gemini 2.5 Flash...")
            
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[
                    types.Part.from_text(prompt),
                    types.Part.from_bytes(data=img_bytes, mime_type=f"image/{img.format.lower() if img.format else 'png'}")
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            
            # Clean and parse response
            clean_text = clean_json_text(response.text)
            print(f"📥 Parsed: {clean_text}")

            json_data = json.loads(clean_text)
            return InvoiceData(**json_data)

    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        raise e
