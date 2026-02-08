import os
import json
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request
from convex import ConvexClient
from dotenv import load_dotenv
import uvicorn
from telegram import Bot, Update

# Load environment variables
load_dotenv()

CONVEX_URL = os.getenv("CONVEX_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not CONVEX_URL:
    raise ValueError("Missing CONVEX_URL environment variable")
if not TELEGRAM_TOKEN:
    raise ValueError("Missing TELEGRAM_TOKEN environment variable")

# Initialize Convex Client
client = ConvexClient(CONVEX_URL)

# Initialize FastAPI App
app = FastAPI()

# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_TOKEN)

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/telegram")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received update: {json.dumps(data)}")
        
        update = Update.de_json(data, bot)
        
        if not update.message or not update.message.text:
            logger.info("Ignoring update without message text")
            return {"status": "ignored"}
            
        message = update.message
        chat_id = message.chat_id
        text = message.text
        user = message.from_user
        
        full_name = user.full_name if user else "Unknown"
        telegram_id = str(user.id) if user else "unknown"

        # 1. Get or Create User in Convex
        logger.info(f"Processing user: {full_name} ({telegram_id})")
        user_id = client.mutation("users:getOrCreateUser", {
            "telegram_id": telegram_id,
            "full_name": full_name
        })
        logger.info(f"Convex User ID: {user_id}")

        # 2. Log Inbound Message
        client.mutation("users:logMessage", {
            "userId": user_id,
            "text": text,
            "direction": "inbound"
        })

        # 3. Determine Response
        response_text = f"You said: {text}"
        if text.startswith("/start"):
            response_text = f"Hello {full_name}! Welcome to Micro CFO."

        # 4. Send Response via Telegram
        await bot.send_message(chat_id=chat_id, text=response_text)

        # 5. Log Outbound Message
        client.mutation("users:logMessage", {
            "userId": user_id,
            "text": response_text,
            "direction": "outbound"
        })

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
