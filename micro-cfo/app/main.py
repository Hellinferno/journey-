import os
from fastapi import FastAPI, Request
from convex import ConvexClient
from dotenv import load_dotenv
import httpx

load_dotenv(".env.local") # Load CONVEX_URL from environment
load_dotenv() # Load other env vars (TELEGRAM_TOKEN)

app = FastAPI()
client = ConvexClient(os.getenv("CONVEX_URL"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    # 1. Extract Data
    if "message" in data:
        chat = data["message"].get("chat", {})
        chat_id = str(chat.get("id", ""))
        text = data["message"].get("text", "")
        sender_name = data["message"].get("from", {}).get("first_name", "Unknown")

        if not chat_id:
             return {"status": "ignored", "reason": "no chat_id"}

        # 2. Call Convex Mutation (Get/Create User)
        # Note: We call the exported function name from users.ts
        user_id = client.mutation("users:getOrCreateUser", {
            "telegram_id": chat_id,
            "full_name": sender_name
        })

        # 3. Log the User's Message in Convex
        client.mutation("users:logMessage", {
            "userId": user_id,
            "text": text,
            "direction": "inbound"
        })

        # 4. Simple "Echo" Response (via Telegram API)
        # In Phase 2, this will be replaced by AI logic
        reply_text = f"Hello {sender_name}, I saved: '{text}' to the Ledger."
        
        async with httpx.AsyncClient() as http_client:
            await http_client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply_text}
            )
            
        # 5. Log Bot's Reply
        client.mutation("users:logMessage", {
            "userId": user_id,
            "text": reply_text,
            "direction": "outbound"
        })

    return {"status": "ok"}
