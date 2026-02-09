# Micro-CFO Telegram Bot

This bot helps you track expenses by analyzing invoices sent via Telegram.

## Features
- 📸 **Invoice OCR**: Extract Vendor, Date, Amount, and GSTIN from images.
- 🤖 **AI Powered**: Uses Google Gemini 1.5 Flash for high accuracy.
- ☁️ **Cloud Database**: Stores data in Convex.

## Quick Start

1.  **Install Requirements** (First time only)
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Bot**
    Double-click `start_bot.bat` OR run:
    ```bash
    start_bot.bat
    ```

## Commands
- `/start`: detailed welcome message.
- `/help`: Usage instructions.
- **Send Photo**: Upload an invoice image to process it.

## Troubleshooting
- If the bot doesn't respond, check the console window for errors.
- Ensure your `.env` file has `TELEGRAM_TOKEN` and `GOOGLE_API_KEY`.
