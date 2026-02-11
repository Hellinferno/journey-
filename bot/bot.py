"""
Micro-CFO Telegram Bot
Analyzes invoice images and provides GST compliance insights
"""
import logging
import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from convex import ConvexClient
from app.ai import analyze_invoice
from app.compliance import audit_invoice

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot_debug.log"),
        logging.StreamHandler()
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Load Configuration
# Railway provides environment variables directly, no .env file needed
# load_dotenv() is only for local development
load_dotenv()  # This will be ignored on Railway if vars are already set

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CONVEX_URL = os.getenv("CONVEX_URL")

# Validate required environment variables
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN environment variable is not set!")
    logger.error(f"Available env vars: {list(os.environ.keys())}")
    raise ValueError("Missing TELEGRAM_TOKEN environment variable. Please set it in Railway Dashboard → Variables tab.")

if not CONVEX_URL:
    logger.error("CONVEX_URL environment variable is not set!")
    raise ValueError("Missing CONVEX_URL environment variable. Please set it in Railway Dashboard → Variables tab.")

logger.info(f"✅ TELEGRAM_TOKEN loaded: {TELEGRAM_TOKEN[:10]}...")
logger.info(f"✅ CONVEX_URL loaded: {CONVEX_URL}")

CONVEX_CLIENT = ConvexClient(CONVEX_URL)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    logger.info(f"User started bot: {user.id} ({user.username})")

    # Register user in Convex
    try:
        CONVEX_CLIENT.mutation("users:getOrCreateUser", {
            "telegram_id": str(user.id),
            "full_name": user.full_name or "Unknown"
        })
    except Exception as e:
        logger.warning(f"Convex Error (getOrCreateUser): {e}")

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Hello {user.first_name}! I'm your Micro-CFO bot. 🤖\n\n"
             f"Send me a photo of an invoice, and I'll analyze it for GST compliance!\n\n"
             f"Type /help to see what I can do."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🤖 *Micro-CFO Bot Help*\n\n"
        "I analyze invoices and check GST compliance automatically.\n\n"
        "*How to use:*\n"
        "1. Send me a photo 📸 of an invoice\n"
        "2. I'll extract vendor, amount, GSTIN, and category\n"
        "3. I'll check compliance and provide insights\n\n"
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
    """Process invoice photos and documents"""
    msg = update.message
    chat_id = msg.chat_id
    
    try:
        # Get file object
        if msg.document:
            file_obj = await msg.document.get_file()
            file_name_ext = msg.document.file_name or "document.jpg"
        elif msg.photo:
            file_obj = await msg.photo[-1].get_file()
            file_name_ext = "photo.jpg"
        else:
            return

        await msg.reply_text("📸 **Analyzing Invoice...**", parse_mode="Markdown")

        # Download to temporary file
        local_path = f"temp_{file_obj.file_id}_{file_name_ext}"
        await file_obj.download_to_drive(local_path)

        try:
            # AI Analysis
            logger.info(f"Analyzing file: {local_path}")
            invoice = analyze_invoice(local_path)
            
            # Compliance Audit
            audit_result = audit_invoice(invoice)
            
            # Save to Convex
            mutation_args = {
                "telegram_id": str(chat_id),
                "vendor": invoice.vendor_name,
                "amount": invoice.total_amount,
                "status": audit_result["status"],
                "category": invoice.category.value,
                "compliance_flags": audit_result["flags"]
            }
            
            if invoice.gstin:
                mutation_args["gstin"] = invoice.gstin
            if invoice.date:
                mutation_args["date"] = invoice.date
            
            CONVEX_CLIENT.mutation("invoices:add", mutation_args)

            # Send response
            status_icons = {
                "compliant": "✅",
                "review_needed": "⚠️",
                "blocked": "🚫"
            }
            status_icon = status_icons.get(audit_result["status"], "⚠️")
            
            reply_text = (
                f"{status_icon} **Analysis Complete**\n"
                f"🏢 Vendor: {invoice.vendor_name}\n"
                f"💰 Amount: ₹{invoice.total_amount}\n"
                f"📂 Category: {invoice.category.value}\n"
                f"🧾 GSTIN: {invoice.gstin or 'N/A'}\n"
            )
            
            if audit_result["flags"]:
                reply_text += "\n**Compliance Notes:**\n"
                for flag in audit_result["flags"]:
                    reply_text += f"• {flag}\n"
            
            # Add citations if available
            if audit_result.get("citations"):
                reply_text += "\n**Legal References:**\n"
                for citation in audit_result["citations"]:
                    reply_text += f"📄 {citation['source']}, Page {citation['page']}\n"
            
            await msg.reply_text(reply_text, parse_mode="Markdown")

        except Exception as ai_error:
            logger.error(f"AI Processing Error: {ai_error}")
            await msg.reply_text(
                f"⚠️ **Extraction Failed**\n"
                f"Error: `{ai_error}`\n\n"
                f"Please ensure your API key has access to Gemini 2.5 Flash.",
                parse_mode="Markdown"
            )
        
        finally:
            # Cleanup temporary file
            if os.path.exists(local_path):
                os.remove(local_path)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Handler Error: {e}\n{error_trace}")
        await msg.reply_text("⚠️ Something went wrong processing your file.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (placeholder for future conversational features)"""
    pass


if __name__ == '__main__':
    logger.info("Starting Micro-CFO Bot...")
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_document_or_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()
