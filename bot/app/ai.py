"""
AI Invoice Analyzer
Uses Google Gemini 2.5 Flash to extract invoice data from images
"""
import google.generativeai as genai
import os
import json
import re
from app.schemas import InvoiceData
from dotenv import load_dotenv

load_dotenv()

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


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
    Analyze invoice image using Google Gemini 2.5 Flash
    
    Args:
        image_path: Path to invoice image file
        
    Returns:
        InvoiceData object with extracted information
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured")

    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
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

Return ONLY the JSON object, no additional text.
"""
        
        # Upload image file
        print("📤 Uploading image to Gemini...")
        uploaded_file = genai.upload_file(image_path)
        
        print("📤 Sending to Gemini 2.5 Flash...")
        response = model.generate_content([prompt, uploaded_file])
        response_text = response.text
        
        # Clean and parse response
        clean_text = clean_json_text(response_text)
        print(f"📥 Parsed: {clean_text}")

        json_data = json.loads(clean_text)
        return InvoiceData(**json_data)

    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        raise e
