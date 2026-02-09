# Bot Not Responding - Troubleshooting Guide

## Issue
The Telegram bot was not responding or showing errors about `gemini-1.5-flash` not found.

## Root Cause
The bot was using cached Python bytecode (`.pyc` files) from an older version of the code that referenced the deprecated `gemini-1.5-flash` model.

## Solution Applied

### 1. Updated Model Name
Changed from `gemini-1.5-flash` → `gemini-2.5-flash` in `app/ai.py`

### 2. Cleared Python Cache
Deleted `__pycache__` folders to force Python to reload the updated code

### 3. Created Fresh Start Script
Created `start_bot_fresh.bat` that clears cache before starting

## How to Start the Bot Correctly

### Option 1: Use the Fresh Start Script (Recommended)
```bash
start_bot_fresh.bat
```

This script:
- Clears all Python cache
- Starts the bot with fresh code
- Ensures no old cached code is used

### Option 2: Manual Start
```bash
# Clear cache first
rmdir /s /q __pycache__
rmdir /s /q app\__pycache__

# Then start bot
python bot.py
```

## Verification

To verify the bot is using the correct model:
```bash
python test_bot_import.py
```

You should see:
```
✅ CORRECT: Using gemini-2.5-flash
```

## Current Status

✅ Code updated to use `gemini-2.5-flash`
✅ Python cache cleared
✅ Fresh start script created
✅ Bot ready to run

## Testing the Bot

1. Start the bot using `start_bot_fresh.bat`
2. Open Telegram and find your bot
3. Send `/start` command
4. Send a photo of an invoice
5. Bot should respond with extracted data

## If Bot Still Not Responding

### Check if bot is running:
- Look for "Application started" in the console
- Check for any error messages

### Check Telegram token:
- Verify `TELEGRAM_TOKEN` in `.env` file
- Token should start with a number followed by colon

### Check API keys:
- Verify `GOOGLE_API_KEY` in `.env` file
- Run `python sanity_check.py` to test API

### Check Convex connection:
- Verify `CONVEX_URL` in `.env` file
- Make sure Convex backend is deployed

## Log Files

Check `bot_debug.log` for detailed error messages:
```bash
type bot_debug.log
```

Look for:
- "AI Processing Error" - indicates Gemini API issues
- "Handler Error" - indicates bot logic issues
- "HTTP Request" - shows bot is communicating with Telegram
