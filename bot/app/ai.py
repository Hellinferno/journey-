"""
AI Invoice Analyzer
Uses Kimi K2.5 via NVIDIA API to extract invoice data from images
"""
import requests
import base64
import os
import json
import re
from app.schemas import InvoiceData
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# NVIDIA API Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


def image_to_base64(image_path: str) -> str:
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


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
    Analyze invoice image using Kimi K2.5
    
    Args:
        image_path: Path to invoice image file
        
    Returns:
        InvoiceData object with extracted information
    """
    if not NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY not configured")

    try:
        # Convert image to base64
        image_base64 = image_to_base64(image_path)
        
        # Determine image format
        with Image.open(image_path) as img:
            image_format = img.format.lower() if img.format else 'jpeg'
        
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
        
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Accept": "application/json"
        }
        
        payload = {
            "model": "moonshotai/kimi-k2.5",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_format};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.1,
            "top_p": 0.95,
            "stream": False
        }
        
        print("📤 Sending to Kimi K2.5...")
        response = requests.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        response_text = result["choices"][0]["message"]["content"]
        
        # Clean and parse response
        clean_text = clean_json_text(response_text)
        print(f"📥 Parsed: {clean_text}")

        json_data = json.loads(clean_text)
        return InvoiceData(**json_data)

    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        raise e
