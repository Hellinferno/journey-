
import logging
import os
import asyncio
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from convex import ConvexClient
from app.ai import analyze_invoice  # Using Gemini based AI analysis

# 1. Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot_debug.log"),
        logging.StreamHandler()
    ]
)
# Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# 2. Load Config
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CONVEX_URL = os.getenv("CONVEX_URL")
CONVEX_CLIENT = ConvexClient(CONVEX_URL)

if not TELEGRAM_TOKEN:
    raise ValueError("Missing TELEGRAM_TOKEN in .env")

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    logger.info(f"User started bot: {user.id} ({user.username})")

    # Register/Get User in Convex
    # Note: We use a fire-and-forget approach or simple mutation here
    try:
        CONVEX_CLIENT.mutation("users:getOrCreateUser", {
            "telegram_id": str(user.id),
            "full_name": user.full_name or "Unknown"
        })
    except Exception as e:
        logger.warning(f"Convex Error (getOrCreateUser): {e}")

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Hello {user.first_name}! I'm your Micro-CFO bot. 🤖\n\nSend me a photo of an invoice, and I'll process it for you!\n\nType /help to see what I can do."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to /help"""
    help_text = (
        "🤖 *Micro-CFO Bot Help*\n\n"
        "I can help you track your expenses by analyzing invoices.\n\n"
        "*How to use me:*\n"
        "1. Send me a photo 📸 or file guarantily of an invoice.\n"
        "2. I will extract the Vendor, Date, Amount, and GSTIN.\n"
        "3. I will save it to your dashboard.\n\n"
        "*Commands:*\n"
        "/start - Restart the bot\n"
        "/help - Show this help message"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_text,
        parse_mode="Markdown"
    )

async def handle_document_or_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes Photos and Documents"""
    msg = update.message
    chat_id = msg.chat_id
    
    try:
        # Get the file object
        if msg.document:
            file_obj = await msg.document.get_file()
            file_name_ext = msg.document.file_name or "document.jpg"
        elif msg.photo:
            # Photos come in multiple sizes, get the largest
            file_obj = await msg.photo[-1].get_file()
            file_name_ext = "photo.jpg"
        else:
            return

        await msg.reply_text("📸 **Analyzing Invoice...**", parse_mode="Markdown")

        # Download to local temp file
        local_path = f"temp_{file_obj.file_id}_{file_name_ext}"
        await file_obj.download_to_drive(local_path)

        try:
            # 1. Run AI Analysis
            logger.info(f"Analyzing file: {local_path}")
            invoice = analyze_invoice(local_path)
            
            # 2. Save to Convex
            CONVEX_CLIENT.mutation("invoices:add", {
                "telegram_id": str(chat_id),
                "vendor": invoice.vendor_name,
                "amount": invoice.total_amount,
                "gstin": invoice.gstin,
                "date": invoice.date if invoice.date else None,
                "status": "processed"
            })

            # 3. Respond
            reply_text = (
                f"✅ **Invoice Saved!**\n"
                f"🏢 Vendor: {invoice.vendor_name}\n"
                f"💰 Amount: ₹{invoice.total_amount}\n"
                f"📅 Date: {invoice.date or 'Not found'}\n"
                f"🧾 GSTIN: {invoice.gstin or 'N/A'}"
            )
            await msg.reply_text(reply_text, parse_mode="Markdown")

        except Exception as ai_error:
            logger.error(f"AI Processing Error: {ai_error}")
            await msg.reply_text(f"⚠️ **Extraction Failed**\nError: `{ai_error}`\n\nPlease ensure your API Key has access to Gemini 1.5 Flash/Pro or a Vision-capable model.", parse_mode="Markdown")
        
        finally:
            # Cleanup
            if os.path.exists(local_path):
                os.remove(local_path)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Handler Error: {e}\n{error_trace}")
        await msg.reply_text("⚠️ Something went wrong processing your file.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo/Log text messages"""
    # This is a good place to add conversational logic later
    # For now, we just acknowledge or ignore non-command text
    pass


async def handle_any(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catch-all for debugging."""
    print(f"DEBUG: Received update: {update}")
    logger.info(f"DEBUG: Received update: {update}")

if __name__ == '__main__':
    print("BOT STARTED RENEWED - DEBUG MODE")
    logger.info("Starting Bot in Polling Mode...")
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_document_or_photo))
    app.add_handler(MessageHandler(filters.ALL, handle_any)) # Catch everything else
    
    app.run_polling()
