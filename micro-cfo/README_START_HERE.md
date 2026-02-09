# 🤖 START YOUR TELEGRAM BOT

## Current Status

✅ **Code is CORRECT** - Using `gemini-2.5-flash`  
✅ **All old bot processes STOPPED**  
✅ **Python cache CLEARED**  
✅ **Environment variables SET**  
✅ **API keys VERIFIED**  

## ⚡ Quick Start (Do This Now)

### Step 1: Start the Bot
Double-click this file:
```
START_BOT_CLEAN.bat
```

### Step 2: Wait for Confirmation
You should see:
```
[4/4] Starting bot...
========================================
 BOT IS STARTING...
 Press Ctrl+C to stop
========================================

Application started
```

### Step 3: Test in Telegram
1. Open Telegram
2. Find your bot
3. Send: `/start`
4. Send a photo of an invoice
5. Bot should respond with extracted data

## 🔍 If Bot Still Not Responding

### Check 1: Is it actually running?
Look at the console window - you should see "Application started"

### Check 2: Are you testing the right bot?
Make sure you're messaging the correct bot in Telegram

### Check 3: Check the logs
Open `bot_debug.log` and look at the LAST few lines:
- Should NOT see "gemini-1.5-flash" errors
- Should see "Analyzing file:" when you send a photo
- Should see successful responses

### Check 4: Run diagnostics
```bash
python show_status.py
```

Should show:
- ✅ MODEL: gemini-2.5-flash (CORRECT)
- ✅ All environment variables set

## 📝 What Was Fixed

The bot was using **cached Python bytecode** from an old version that referenced deprecated models. 

**The fix:**
1. Updated `app/ai.py` to use `gemini-2.5-flash`
2. Stopped all old bot processes
3. Cleared all Python cache
4. Created `START_BOT_CLEAN.bat` that ensures fresh start

## 🛠️ Useful Commands

| Command | Purpose |
|---------|---------|
| `START_BOT_CLEAN.bat` | **Start bot (USE THIS)** |
| `STOP_BOT.bat` | Stop all bot processes |
| `python show_status.py` | Check current status |
| `python quick_test.py` | Verify correct model |
| `python diagnose_bot.py` | Full diagnostic |

## ❓ Common Issues

### "Bot not responding to /start"
- Check if bot is actually running (console should show "Application started")
- Verify you're messaging the correct bot
- Check Telegram token in `.env` file

### "Bot responds but invoice extraction fails"
- Check `bot_debug.log` for errors
- Run `python sanity_check.py` to test Gemini API
- Verify image is clear and readable

### "Still seeing old model errors in logs"
- Make sure you used `START_BOT_CLEAN.bat` not `python bot.py`
- Run `STOP_BOT.bat` first, then `START_BOT_CLEAN.bat`

## 📊 Verification

Before starting, verify everything is correct:

```bash
python quick_test.py
```

Should output:
```
✅ SUCCESS: Bot will use gemini-2.5-flash
```

## 🎯 Next Steps

1. **Start the bot**: `START_BOT_CLEAN.bat`
2. **Test with /start command** in Telegram
3. **Send an invoice photo** to test extraction
4. **Check Convex dashboard** to see saved data

---

**Your bot is ready! Start it now with `START_BOT_CLEAN.bat`** 🚀
