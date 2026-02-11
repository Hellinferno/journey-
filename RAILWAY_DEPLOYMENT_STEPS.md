# Railway Deployment - Step by Step

## 🚨 CRITICAL ISSUE

Railway is detecting your project as Node.js instead of Python because it's running from the repository root (`/`) instead of the `bot/` folder.

**Error you're seeing:**
```
Error: Cannot find module '/app/index.js'
/bin/bash: line 1: pip: command not found
```

## ✅ THE FIX (3 Steps)

### Step 1: Set Root Directory (REQUIRED)

**You MUST do this in Railway Dashboard - config files alone won't work!**

1. Open: https://railway.app/dashboard
2. Click on your bot service
3. Click **"Settings"** tab (top navigation)
4. Scroll to **"Service Settings"** section
5. Find **"Root Directory"** field
6. Type: `bot`
7. Press Enter or click outside the field to save

**Why this is required:**
- Your repository structure is: `journey/bot/` and `journey/dashboard/`
- Without setting Root Directory, Railway runs from `journey/` (root)
- Railway sees no Python files at root, detects as Node.js
- With Root Directory set to `bot`, Railway runs from `journey/bot/`
- Railway finds `bot.py`, `requirements.txt`, detects as Python ✅

### Step 2: Add Environment Variables

Still in Railway Dashboard:

1. Click **"Variables"** tab
2. Click **"New Variable"** button
3. Add these 3 variables:

**Variable 1:**
```
Name: TELEGRAM_TOKEN
Value: <get from @BotFather on Telegram>
```

**Variable 2:**
```
Name: GOOGLE_API_KEY
Value: <get from Google AI Studio>
```

**Variable 3:**
```
Name: CONVEX_URL
Value: <get from Convex Dashboard>
```

**Where to get these values:**
- **TELEGRAM_TOKEN**: Message [@BotFather](https://t.me/botfather) → `/newbot` → copy token
- **GOOGLE_API_KEY**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) → Create API Key
- **CONVEX_URL**: Open Convex Dashboard → Your project → Copy deployment URL

### Step 3: Redeploy

1. Click **"Deployments"** tab
2. Click **"Redeploy"** on the latest deployment
3. Watch the build logs

## ✅ Expected Build Output (Success)

After setting Root Directory to `bot`, you should see:

```
✅ Detected Python 3.11 project
✅ Installing Python dependencies
✅ Running: pip install -r requirements.txt
✅ Build complete
✅ Starting: python bot.py
✅ Bot connected to Telegram
✅ Bot is running
```

## ❌ What You're Seeing Now (Before Fix)

```
❌ Detected Node.js project (WRONG!)
❌ Looking for /app/index.js (doesn't exist)
❌ /bin/bash: pip: command not found
❌ Error: Cannot find module '/app/index.js'
```

## 📊 Repository Structure

```
journey/                    ← Railway is running from HERE (wrong!)
├── bot/                    ← Railway should run from HERE (correct!)
│   ├── bot.py             ← Python bot entry point
│   ├── requirements.txt   ← Python dependencies
│   ├── runtime.txt        ← Python 3.11
│   ├── Procfile           ← Start command
│   ├── nixpacks.toml      ← Build config
│   └── railway.json       ← Deploy config
└── dashboard/             ← Next.js dashboard (separate)
```

## 🔍 Verification Checklist

After completing all steps, verify:

- [ ] Root Directory is set to `bot` in Railway Settings
- [ ] 3 environment variables are added (TELEGRAM_TOKEN, GOOGLE_API_KEY, CONVEX_URL)
- [ ] Build logs show "Detected Python 3.11 project"
- [ ] Build logs show "pip install -r requirements.txt" succeeds
- [ ] Deploy logs show "python bot.py" running
- [ ] No errors about "index.js" or "pip: command not found"

## 🐛 Troubleshooting

### Still seeing "Cannot find module '/app/index.js'"?

**Problem:** Root Directory not set

**Solution:**
1. Go to Railway Dashboard → Settings
2. Scroll to "Root Directory"
3. Ensure it says `bot` (not empty, not `/`, not `./bot`)
4. If not set, type `bot` and save
5. Redeploy

### Still seeing "pip: command not found"?

**Problem:** Railway still detecting as Node.js

**Solution:**
1. Verify Root Directory is `bot`
2. Check that `bot/runtime.txt` exists in your repository
3. Check that `bot/requirements.txt` exists
4. Redeploy

### Bot not responding to messages?

**Problem:** Environment variables not set or incorrect

**Solution:**
1. Go to Railway Dashboard → Variables
2. Verify all 3 variables are present
3. Check for typos in variable names (case-sensitive!)
4. Verify token with @BotFather
5. Redeploy

## 📝 Summary

**The ONE critical step:** Set Root Directory to `bot` in Railway Dashboard Settings.

Everything else (Dockerfile, nixpacks.toml, railway.json) is already configured in your repository. Railway just needs to know to run from the `bot/` folder instead of the root.

---

**Next Action:** Go to Railway Dashboard → Settings → Root Directory → `bot` → Redeploy
