# Fix Railway Bot Deployment Error

## ❌ Error You're Seeing

```
Error: Cannot find module '/app/index.js'
code: 'MODULE_NOT_FOUND'
```

## 🔍 Root Cause

Railway is trying to run from the repository root (`/app/`) instead of the `bot/` folder. It's looking for `index.js` (Node.js) but your bot is Python (`bot.py`).

## ✅ Solution: Configure Railway Root Directory

### Step 1: Go to Railway Dashboard

1. Open: https://railway.app/dashboard
2. Select your bot project
3. Click on your service

### Step 2: Update Root Directory

1. Click **"Settings"** tab
2. Scroll to **"Service Settings"**
3. Find **"Root Directory"**
4. Set to: `bot`
5. Click **"Save"**

### Step 3: Verify Build Configuration

Still in Settings, check:

**Build:**
- **Builder:** Nixpacks (auto-detect)
- **Build Command:** `pip install -r requirements.txt` (optional, auto-detected)

**Deploy:**
- **Start Command:** `python bot.py`
- **Watch Paths:** Leave empty or set to `bot/**`

### Step 4: Set Environment Variables

1. Click **"Variables"** tab
2. Ensure these are set:
   - `TELEGRAM_TOKEN` = your bot token
   - `GOOGLE_API_KEY` = your Gemini API key
   - `CONVEX_URL` = `https://woozy-chihuahua-345.convex.cloud`

### Step 5: Redeploy

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on latest deployment
3. OR: Push a new commit to trigger deployment

## 🔧 Alternative: Create New Railway Service

If updating doesn't work, create a fresh service:

### Option A: From GitHub

1. Go to Railway Dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Configure:
   - **Root Directory:** `bot`
   - **Start Command:** `python bot.py`
6. Add environment variables (see Step 4 above)
7. Deploy

### Option B: Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Set root directory
railway up --service bot

# Or deploy with specific directory
cd bot
railway up
```

## 📋 Verification Checklist

After deployment, verify:

- [ ] Root Directory set to: `bot`
- [ ] Start Command: `python bot.py`
- [ ] Environment variables set (3 total)
- [ ] Build logs show: "Installing Python dependencies"
- [ ] Deploy logs show: "Bot started successfully"
- [ ] No errors in logs

## 🔍 Check Deployment Logs

1. Go to Railway Dashboard → Your Service
2. Click **"Deployments"** tab
3. Click on latest deployment
4. Check **"Build Logs"** and **"Deploy Logs"**

**Look for:**
- ✅ "Installing dependencies from requirements.txt"
- ✅ "Starting bot..."
- ✅ "Bot is running"
- ❌ Any Python errors or missing modules

## 🐛 Common Issues

### Issue: "No such file or directory: 'bot.py'"

**Cause:** Root directory not set to `bot`

**Fix:**
- Settings → Root Directory → `bot`
- Redeploy

### Issue: "ModuleNotFoundError: No module named 'telegram'"

**Cause:** Dependencies not installed

**Fix:**
- Check `requirements.txt` exists in `bot/` folder
- Verify Build Command runs: `pip install -r requirements.txt`
- Redeploy

### Issue: "TELEGRAM_TOKEN not found"

**Cause:** Environment variables not set

**Fix:**
- Variables tab → Add all 3 environment variables
- Redeploy

### Issue: Still looking for index.js

**Cause:** Railway detecting as Node.js project

**Fix:**
1. Settings → Builder → Select "Nixpacks"
2. Settings → Start Command → `python bot.py`
3. Ensure `runtime.txt` exists with `python-3.11`
4. Redeploy

## 📊 Expected Deployment Flow

When correctly configured:

1. **Build Phase:**
   ```
   → Detected Python project
   → Installing Python 3.11
   → Installing dependencies from requirements.txt
   → Build complete
   ```

2. **Deploy Phase:**
   ```
   → Starting service
   → Running: python bot.py
   → Bot connected to Telegram
   → Bot is running
   ```

3. **Runtime:**
   ```
   → Bot listening for messages
   → Processing invoices
   → Storing data in Convex
   ```

## ✅ Success Indicators

Bot is working when:
- ✅ Railway shows "Active" status (green)
- ✅ Deploy logs show "Bot is running"
- ✅ No errors in logs
- ✅ Bot responds to Telegram messages
- ✅ Invoices are processed and stored

## 🆘 Still Not Working?

### Check These:

1. **Railway Service Settings:**
   - Root Directory: `bot` ✅
   - Start Command: `python bot.py` ✅
   - Builder: Nixpacks ✅

2. **Environment Variables:**
   - TELEGRAM_TOKEN: Set ✅
   - GOOGLE_API_KEY: Set ✅
   - CONVEX_URL: Set ✅

3. **Files in bot/ folder:**
   - bot.py: Exists ✅
   - requirements.txt: Exists ✅
   - Procfile: Exists ✅
   - runtime.txt: Exists ✅

4. **Logs:**
   - Build logs: No errors ✅
   - Deploy logs: Bot started ✅
   - Runtime logs: No crashes ✅

## 📞 Quick Fix Summary

**The ONE thing you need to do:**

Go to Railway → Settings → Root Directory → Set to `bot` → Save → Redeploy

That's it! Railway will then find `bot.py` instead of looking for `index.js`.

---

**Next Step:** Set Root Directory to `bot` in Railway Settings and redeploy.
