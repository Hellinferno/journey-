"""
AI Invoice Analyzer
Uses NVIDIA APIs (Kimi K2.5, GPT-OSS) or Google Gemini to extract invoice data from images
"""
import google.generativeai as genai
import requests
import base64
import os
import json
import re
from openai import OpenAI
from app.schemas import InvoiceData
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_OPENAI_KEY = os.getenv("NVIDIA_OPENAI_KEY")
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


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


def analyze_invoice_with_nvidia_openai(image_path: str) -> InvoiceData:
    """
    Analyze invoice using NVIDIA OpenAI-compatible API (GPT-OSS-120B)
    
    Args:
        image_path: Path to invoice image file
        
    Returns:
        InvoiceData object with extracted information
    """
    if not NVIDIA_OPENAI_KEY:
        raise ValueError("NVIDIA_OPENAI_KEY not configured")

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
        
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=NVIDIA_OPENAI_KEY
        )
        
        print("📤 Sending to NVIDIA GPT-OSS-120B...")
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
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
            temperature=1,
            top_p=1,
            max_tokens=4096,
            stream=False
        )
        
        response_text = completion.choices[0].message.content
        
        # Clean and parse response
        clean_text = clean_json_text(response_text)
        print(f"📥 Parsed: {clean_text}")

        json_data = json.loads(clean_text)
        return InvoiceData(**json_data)

    except Exception as e:
        print(f"❌ NVIDIA OpenAI Analysis Error: {e}")
        raise e


def analyze_invoice_with_nvidia(image_path: str) -> InvoiceData:
    """
    Analyze invoice using NVIDIA Kimi K2.5
    
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
            "max_tokens": 16384,
            "temperature": 1.00,
            "top_p": 1.00,
            "stream": False,
            "chat_template_kwargs": {"thinking": True}
        }
        
        print("📤 Sending to NVIDIA Kimi K2.5...")
        response = requests.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        response_text = result["choices"][0]["message"]["content"]
        
        # Clean and parse response
        clean_text = clean_json_text(response_text)
        print(f"📥 Parsed: {clean_text}")

        json_data = json.loads(clean_text)
        return InvoiceData(**json_data)

    except Exception as e:
        print(f"❌ NVIDIA Analysis Error: {e}")
        raise e


def analyze_invoice_with_gemini(image_path: str) -> InvoiceData:
    """
    Analyze invoice using Google Gemini 2.5 Flash
    
    Args:
        image_path: Path to invoice image file
        
    Returns:
        InvoiceData object with extracted information
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured")

    try:
        # Initialize Gemini model - using stable version
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
        
        print("📤 Sending to Gemini 1.5 Flash...")
        response = model.generate_content([prompt, uploaded_file])
        response_text = response.text
        
        # Clean and parse response
        clean_text = clean_json_text(response_text)
        print(f"📥 Parsed: {clean_text}")

        json_data = json.loads(clean_text)
        return InvoiceData(**json_data)

    except Exception as e:
        print(f"❌ Gemini Analysis Error: {e}")
        raise e


def analyze_invoice(image_path: str) -> InvoiceData:
    """
    Analyze invoice image using available AI provider
    Priority: NVIDIA OpenAI GPT-OSS > NVIDIA Kimi K2.5 > Google Gemini 1.5 Flash
    
    Args:
        image_path: Path to invoice image file
        
    Returns:
        InvoiceData object with extracted information
    """
    # Try NVIDIA OpenAI first if API key is available
    if NVIDIA_OPENAI_KEY:
        try:
            return analyze_invoice_with_nvidia_openai(image_path)
        except Exception as nvidia_openai_error:
            print(f"⚠️ NVIDIA OpenAI failed: {nvidia_openai_error}")
            print("🔄 Trying NVIDIA Kimi K2.5...")
    
    # Try NVIDIA Kimi K2.5 if API key is available
    if NVIDIA_API_KEY:
        try:
            return analyze_invoice_with_nvidia(image_path)
        except Exception as nvidia_error:
            print(f"⚠️ NVIDIA Kimi failed: {nvidia_error}")
            print("🔄 Falling back to Gemini...")
    
    # Fallback to Gemini
    if GOOGLE_API_KEY:
        return analyze_invoice_with_gemini(image_path)
    
    # No API keys available
    raise ValueError("No AI API keys configured. Please set NVIDIA_OPENAI_KEY, NVIDIA_API_KEY, or GOOGLE_API_KEY")
