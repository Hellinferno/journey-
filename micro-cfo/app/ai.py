
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
    Sends image to Google Gemini 1.5 Flash and forces a JSON response 
    matching our InvoiceData schema.
    """
    
    # 2. Load the Model with Schema Enforcement
    # We tell Gemini: "Your output MUST follow this specific structure."
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "response_mime_type": "application/json", 
            "response_schema": InvoiceData  # Pass your Pydantic class directly!
        }
    )

    # 3. Load Image
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Failed to open image: {e}")

    # 4. Define the Prompt
    prompt = """
    Extract data from this Indian invoice. 
    - Handle Hindi/English text accurately.
    - If the GSTIN is missing, leave it null.
    - Calculate tax_amount if not explicitly stated (Total - Subtotal).
    """

    # 5. Generate Content
    try:
        response = model.generate_content([prompt, img])
        
        # 6. Parse Response
        # Gemini returns a JSON string, which we convert back to our Pydantic object
        json_data = json.loads(response.text)
        invoice = InvoiceData(**json_data)
        return invoice
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        # Return a safe fallback or re-raise
        raise e
