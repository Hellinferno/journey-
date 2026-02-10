"""
AI Invoice Analyzer
Uses Google Gemini to extract invoice data from images
"""
import google.generativeai as genai
import os
import json
import re
from app.schemas import InvoiceData
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


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
            response = model.generate_content([prompt, img])
            
            # Clean and parse response
            clean_text = clean_json_text(response.text)
            print(f"📥 Parsed: {clean_text}")

            json_data = json.loads(clean_text)
            return InvoiceData(**json_data)

    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        raise e
