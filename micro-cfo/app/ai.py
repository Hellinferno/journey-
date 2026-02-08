
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

def analyze_invoice(image_path: str) -> InvoiceData:
    """
    Sends image to Google Gemini 1.5 Flash and parses the JSON response.
    """
    
    # 2. Load the Model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "response_mime_type": "application/json"
        }
    )

    # 3. Load Image
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Failed to open image: {e}")

    # 4. Define the Prompt with explicit schema in text
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

    # 5. Generate Content
    try:
        response = model.generate_content([prompt, img])
        
        # 6. Parse Response
        try:
            # Clean possible markdown wrap
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip("` \n")
            
            json_data = json.loads(raw_text)
            invoice = InvoiceData(**json_data)
            return invoice
        except Exception as parse_error:
            print(f"JSON Parse Error. Raw Response: {response.text}")
            raise parse_error

    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise e
