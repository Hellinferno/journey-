import os
import json
from fastapi import FastAPI, Request
from convex import ConvexClient
from dotenv import load_dotenv
import httpx
from app.ocr import analyze_invoice
import tempfile

load_dotenv(".env.local") # Load CONVEX_URL from environment
load_dotenv() # Load other env vars (TELEGRAM_TOKEN)

app = FastAPI()
client = ConvexClient(os.getenv("CONVEX_URL"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    if "message" in data:
        chat = data["message"].get("chat", {})
        chat_id = str(chat.get("id", ""))
        text = data["message"].get("text", "")
        sender_name = data["message"].get("from", {}).get("first_name", "Unknown")
        photo = data["message"].get("photo")

        if not chat_id:
             return {"status": "ignored", "reason": "no chat_id"}

        # 1. Get or Create User
        user_id = client.mutation("users:getOrCreateUser", {
            "telegram_id": chat_id,
            "full_name": sender_name
        })

        reply_text = ""

        # 2. Handle Photo (Invoice)
        if photo:
            # Telegram sends multiple sizes; take the last one (largest)
            file_id = photo[-1]["file_id"]
            
            async with httpx.AsyncClient() as http_client:
                # Get File Path
                file_info_resp = await http_client.get(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
                )
                file_path = file_info_resp.json()["result"]["file_path"]
                
                # Download File
                file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
                image_resp = await http_client.get(file_url)
                
                # Temporarily save image
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(image_resp.content)
                    tmp_path = tmp.name

            # Log receipt
            client.mutation("users:logMessage", {
                "userId": user_id,
                "text": "[Photo] Analyzing Invoice...",
                "direction": "inbound"
            })
            await send_telegram_message(chat_id, "Analyzing your invoice... please wait.")

            # Analyze with Gemini
            try:
                invoice_data = analyze_invoice(tmp_path)
                # Cleanup temp file
                os.remove(tmp_path)
                
                # Format success message
                reply_text = (
                    f"✅ **Invoice Analyzed!**\n\n"
                    f"Vendor: {invoice_data.vendor_name}\n"
                    f"Date: {invoice_data.date}\n"
                    f"Total: {invoice_data.currency} {invoice_data.total_amount}\n"
                    f"Tax: {invoice_data.tax_amount}"
                )
                
                # Save structured data (TODO: Store in a separate Convex table later)
                # For now, just log as text
                client.mutation("users:logMessage", {
                    "userId": user_id,
                    "text": json.dumps(invoice_data.model_dump(), default=str),
                    "direction": "inbound" 
                })

            except Exception as e:
                reply_text = f"❌ Error analyzing invoice: {str(e)}"
                os.remove(tmp_path)

        # 3. Handle Text
        elif text:
            # Log text
            client.mutation("users:logMessage", {
                "userId": user_id,
                "text": text,
                "direction": "inbound"
            })
            reply_text = f"Hello {sender_name}, send me a photo of an invoice to analyze!"

        # 4. Send Reply
        if reply_text:
            await send_telegram_message(chat_id, reply_text)
            
            # Log Bot's Reply
            client.mutation("users:logMessage", {
                "userId": user_id,
                "text": reply_text,
                "direction": "outbound"
            })

    return {"status": "ok"}

async def send_telegram_message(chat_id: str, text: str):
    async with httpx.AsyncClient() as http_client:
        await http_client.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        )
