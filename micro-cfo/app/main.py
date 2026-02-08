import os
import httpx
from fastapi import FastAPI, Request
from convex import ConvexClient
from app.ocr import analyze_invoice
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "micro-cfo-bot"}

client = ConvexClient(os.getenv("CONVEX_URL"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def download_telegram_file(file_id: str) -> str:
    """Helper to download file from Telegram"""
    async with httpx.AsyncClient() as http:
        # 1. Get File Path
        res = await http.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}")
        file_path = res.json()["result"]["file_path"]
        
        # 2. Download Content
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        image_res = await http.get(file_url)
        
        # 3. Save locally
        local_filename = "temp_invoice.jpg"
        with open(local_filename, "wb") as f:
            f.write(image_res.content)
            
        return local_filename

async def send_reply(chat_id: str, text: str):
    """Helper to send message"""
    async with httpx.AsyncClient() as http:
        await http.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    if "message" in data and "photo" in data["message"]:
        msg = data["message"]
        chat_id = str(msg["chat"]["id"])
        
        # 1. Acknowledge Receipt
        await send_reply(chat_id, "📸 **Analyzing Invoice...**")
        
        try:
            # 2. Get highest res photo
            photo_id = msg["photo"][-1]["file_id"]
            local_path = await download_telegram_file(photo_id)
            
            # 3. Run Gemini OCR
            invoice = analyze_invoice(local_path)
            
            if invoice:
                # 4. Save to Convex
                client.mutation("invoices:add", {
                    "telegram_id": chat_id,
                    "vendor": invoice.vendor_name,
                    "amount": invoice.total_amount,
                    "gstin": invoice.gstin,
                    "date": invoice.date,
                    "status": "processed"
                })
                
                # 5. Reply with Success
                reply = (
                    f"✅ **Invoice Saved!**\n"
                    f"🏢 Vendor: {invoice.vendor_name}\n"
                    f"💰 Amount: ₹{invoice.total_amount}\n"
                    f"📅 Date: {invoice.date or 'Not found'}\n"
                    f"🧾 GSTIN: {invoice.gstin or 'N/A'}"
                )
                await send_reply(chat_id, reply)
            else:
                await send_reply(chat_id, "⚠️ Could not read invoice details.")
                
            # Cleanup
            if os.path.exists(local_path):
                os.remove(local_path)
                
        except Exception as e:
            print(f"Error: {e}")
            await send_reply(chat_id, "⚠️ Something went wrong processing the image.")

    return {"status": "ok"}
