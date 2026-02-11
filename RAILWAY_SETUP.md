# Railway Bot Deployment Guide

## 🚨 CRITICAL: Root Directory Configuration

Railway is trying to run from the repository root instead of the `bot/` folder, causing the "Cannot find module '/app/index.js'" error.

## Required Steps

### 1. Set Root Directory in Railway Dashboard

1. Go to: https://railway.app/dashboard
2. Select your bot project/service
3. Click **"Settings"** tab
4. Find **"Root Directory"** field
5. Enter: `bot`
6. Click **"Save"**

### 2. Configure Environment Variables

In Railway Dashboard → Variables tab, add these 3 required variables:

```
TELEGRAM_TOKEN=<your_telegram_bot_token>
GOOGLE_API_KEY=<your_google_gemini_api_key>
CONVEX_URL=<your_convex_deployment_url>
```

**How to get these values:**
- **TELEGRAM_TOKEN**: Talk to [@BotFather](https://t.me/botfather) on Telegram, use `/newbot`
- **GOOGLE_API_KEY**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **CONVEX_URL**: Get from your Convex Dashboard

### 3. Verify Build Configuration

In Settings, ensure:
- **Builder**: Nixpacks (auto-detect)
- **Start Command**: `python bot.py`

### 4. Redeploy

Go to Deployments tab → Click "Redeploy"

## Expected Build Output

After correct configuration:

```
✅ Detected Python 3.11 project
✅ Installing dependencies from requirements.txt
✅ Build complete
✅ Starting: python bot.py
✅ Bot connected to Telegram
```

## Repository Structure

```
journey/
├── bot/              ← Set Railway Root Directory HERE
│   ├── bot.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── nixpacks.toml
│   └── railway.json
└── dashboard/
```

## Troubleshooting

### Still seeing "Cannot find module '/app/index.js'"?
- Root Directory is not set to `bot`
- Go to Settings → Root Directory → `bot` → Save → Redeploy

### "pip: command not found"?
- Railway is detecting as Node.js project
- Ensure Root Directory is set to `bot`
- Check that `bot/runtime.txt` exists with `python-3.11`

### Bot not responding?
- Check environment variables are set correctly
- View deployment logs for errors
- Verify Telegram token with @BotFather

## Files in bot/ folder

- ✅ `bot.py` - Main bot entry point
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version (3.11)
- ✅ `Procfile` - Start command
- ✅ `nixpacks.toml` - Nixpacks configuration
- ✅ `railway.json` - Railway configuration
- ✅ `Dockerfile` - Docker build instructions

---

**TL;DR:** Railway Settings → Root Directory → `bot` → Save → Add 3 environment variables → Redeploy
