import os
import json
import httpx
import pytesseract
from PIL import Image
from app.schemas import InvoiceData
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configure Tesseract path for Windows
tesseract_cmd = os.getenv("TESSERACT_CMD")
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def analyze_invoice(image_path: str) -> InvoiceData:
    """
    Two-step OCR approach:
    1. Use Tesseract to extract text from image
    2. Use Groq LLM to parse text into structured data
    """
    
    try:
        # Step 1: Extract text using Tesseract OCR
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img, lang='eng+hin')
        
        if not extracted_text.strip():
            print("OCR: No text extracted from image")
            return None
        
        print(f"OCR Extracted: {extracted_text[:200]}...")
        
        # Step 2: Use Groq to parse the extracted text
        prompt = f"""
        Analyze this invoice text and extract the following fields. Return ONLY a valid JSON object (no markdown, no explanation):
        {{
            "vendor_name": "string",
            "invoice_number": "string or null",
            "date": "YYYY-MM-DD or null",
            "total_amount": float,
            "tax_amount": float (defaults to 0),
            "gstin": "string or null",
            "currency": "string (defaults to INR)"
        }}
        
        Invoice Text:
        {extracted_text}
        
        If the text is in Hindi, translate relevant fields to English.
        Ensure total_amount is purely numeric.
        Return ONLY the JSON object.
        """

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Make API request to Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        
        result = response.json()
        
        # Parse response
        response_text = result["choices"][0]["message"]["content"].strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        json_data = json.loads(response_text)
        return InvoiceData(**json_data)
        
    except Exception as e:
        import traceback
        error_msg = f"OCR Failed: {e}\n{traceback.format_exc()}"
        print(error_msg)
        with open("ocr_debug.log", "a") as f:
            f.write(error_msg + "\n")
        return None
