
import google.generativeai as genai
import os
import json
from app.schemas import InvoiceData
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 1. Configure the API
if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

import re
import shutil

# Try to find Tesseract in PATH if not already configured
if not shutil.which("tesseract"):
    # Fallback to common Windows path only if not found in PATH
    default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(default_path):
        pytesseract.pytesseract.tesseract_cmd = default_path

def clean_json_text(text: str) -> str:
    """Robustly extracts JSON object from any AI response text."""
    # 1. Strip markdown code blocks
    text = re.sub(r"```(json)?", "", text).replace("```", "").strip()
    
    # 2. Find the actual JSON object (start at first '{', end at last '}')
    start = text.find("{")
    end = text.rfind("}")
    
    if start != -1 and end != -1:
        return text[start:end+1]
    return text

def extract_text_with_tesseract(image_path: str) -> str:
    """Fallback: Extract text using local Tesseract OCR."""
    print("Falling back to Tesseract OCR...")
    try:
        # Check if tesseract is actually available before trying
        if not shutil.which("tesseract") and not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            raise FileNotFoundError("Tesseract not found in PATH or default location.")
            
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        print(f"Tesseract Error: {e}")
        raise e

def analyze_invoice(image_path: str) -> InvoiceData:
    """
    Sends image to Google Gemini 1.5 Flash and parses the JSON response.
    """
    
    # List of models to try in order
    model_names = [
        "models/gemini-pro-preview-12-2025",
        "models/gemini-3-pro-preview-12-2025",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-flash-latest",
        "models/gemini-1.5-pro-latest",
        "models/gemini-1.5-pro",
        "models/gemini-pro",
        "models/gemini-1.5-flash-001",
        "models/gemini-1.5-flash-002",
        "models/gemini-1.5-pro-001",
        "models/gemini-1.5-pro-002",
        "models/gemini-2.0-flash-exp",
        "models/gemini-1.0-pro",
        "models/gemini-1.0-pro-latest"
    ]

    last_error = None

    # 3. Load Image
    try:
        with Image.open(image_path) as img:
            prompt = """
            Extract data from this Indian invoice. 
            Return a JSON object matching this structure:
            {
                "vendor_name": "string",
                "invoice_number": "string or null",
                "date": "string or null",
                "total_amount": float,
                "tax_amount": float,
                "gstin": "string or null",
                "currency": "string"
            }

            - Handle Hindi/English text accurately.
            - If the GSTIN is missing, leave it null.
            - Calculate tax_amount if not explicitly stated (Total - Subtotal).
            """

            for model_name in model_names:
                try:
                    print(f"Trying model: {model_name}")
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config={
                            "response_mime_type": "application/json"
                        }
                    )
                    response = model.generate_content([prompt, img])
                    break # Success
                except Exception as e:
                    print(f"Model {model_name} failed: {e}")
                    last_error = e
            else:
                # Loop finished without success (All Vision models failed)
                print(f"Gemini Vision failed. Last error: {last_error}")
                print("Attempting Hybrid Fallback: Tesseract OCR -> Gemini Text")
                
                # 1. Local OCR
                extracted_text = extract_text_with_tesseract(image_path)
                if not extracted_text.strip():
                    raise Exception("Tesseract extracted no text from image.")

                # 2. Gemini Text Analysis (Try multiple models)
                fallback_text_models = [
                    "models/gemini-1.5-flash",
                    "models/gemini-1.5-flash-latest",
                    "models/gemini-pro",
                    "models/gemini-1.5-pro",
                    "models/gemini-1.0-pro-latest",
                    "models/gemini-pro-preview-12-2025"
                ]
                
                response = None
                text_error = None

                for text_model_name in fallback_text_models:
                    try:
                        print(f"Sending OCR text to {text_model_name}...")
                        text_model = genai.GenerativeModel(
                            model_name=text_model_name,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        
                        text_prompt = f"""
                        Extract data from this OCR text of an Indian invoice.
                        Return JSON matching:
                        {{
                            "vendor_name": "string",
                            "invoice_number": "string or null",
                            "date": "string or null",
                            "total_amount": float,
                            "tax_amount": float,
                            "gstin": "string or null",
                            "currency": "string"
                        }}
                        
                        OCR Text:
                        {extracted_text}
                        """
                        
                        response = text_model.generate_content(text_prompt)
                        if response:
                            break
                    except Exception as e:
                        print(f"Text Model {text_model_name} failed: {e}")
                        text_error = e
                
                if not response:
                    raise Exception(f"All fallback text models failed. Last error: {text_error}")

        # 6. Parse Response (Outside 'with' block to ensure file is closed)
        try:
            # Robust Parsing
            raw_response = response.text
            clean_text = clean_json_text(raw_response)
            print(f"📥 Parsed JSON: {clean_text}")

            json_data = json.loads(clean_text)
            invoice = InvoiceData(**json_data)
            return invoice
        except Exception as parse_error:
            print(f"JSON Parse Error. Raw Response: {response.text}")
            raise parse_error

    except Exception as e:
        print(f"Gemini API/File Error: {e}")
        raise e
