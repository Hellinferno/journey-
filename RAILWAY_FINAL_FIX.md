# Railway Deployment - Final Fix

## What I Fixed

1. ✅ Changed Railway builder from NIXPACKS to DOCKERFILE
2. ✅ Updated Dockerfile with proper Python base image and dependencies
3. ✅ Added .dockerignore to exclude unnecessary files
4. ✅ Pushed all changes to GitHub

## What YOU Must Do Now

Railway requires **manual configuration in the dashboard** that cannot be set via config files.

### Step 1: Set Root Directory (CRITICAL)

1. Go to: https://railway.app/dashboard
2. Click on your bot service
3. Click **"Settings"** tab
4. Find **"Root Directory"** field
5. Type: `bot`
6. Press Enter to save

**Why this is required:**
- Your code is in `journey/bot/` folder
- Railway needs to know to run from `bot/` not from root
- Without this, Railway can't find your Dockerfile or Python files

### Step 2: Verify Builder Settings

Still in Settings tab:

1. Find **"Builder"** section
2. It should now say: **"Dockerfile"**
3. If it says "Nixpacks" or "Auto", change it to **"Dockerfile"**

### Step 3: Add Environment Variables

Click **"Variables"** tab and add these 3 variables:

```
TELEGRAM_TOKEN=<your_bot_token_from_@BotFather>
GOOGLE_API_KEY=<your_gemini_api_key>
CONVEX_URL=<your_convex_deployment_url>
```

### Step 4: Redeploy

1. Click **"Deployments"** tab
2. Click **"Redeploy"** on latest deployment
3. Watch the build logs

## Expected Build Output (Success)

After setting Root Directory to `bot`, you should see:

```
✅ Building with Dockerfile
✅ FROM python:3.11-slim
✅ Installing system dependencies (gcc)
✅ Installing Python dependencies
✅ Successfully installed python-telegram-bot google-generativeai convex...
✅ Build complete
✅ Starting: python bot.py
✅ Bot is running
```

## Why Previous Attempts Failed

The error you saw:
```
/bin/bash: line 1: pip: command not found
node_modules/cache
```

This happened because:
1. Railway was running from repository root (not `bot/` folder)
2. Railway detected Node.js project (saw `dashboard/package.json`)
3. Railway used Node.js base image (no Python, no pip)
4. Dockerfile commands failed because pip doesn't exist in Node.js image

## The Fix

By setting Root Directory to `bot`:
- Railway runs from `journey/bot/` folder
- Railway finds `Dockerfile` in `bot/` folder
- Railway uses Dockerfile builder (Python 3.11 base image)
- pip exists, dependencies install successfully ✅

## Verification Checklist

After completing all steps:

- [ ] Root Directory is set to `bot` in Railway Settings
- [ ] Builder is set to "Dockerfile" in Railway Settings
- [ ] 3 environment variables added (TELEGRAM_TOKEN, GOOGLE_API_KEY, CONVEX_URL)
- [ ] Redeployed the service
- [ ] Build logs show "Building with Dockerfile"
- [ ] Build logs show "FROM python:3.11-slim"
- [ ] Build logs show "Successfully installed" Python packages
- [ ] Deploy logs show "python bot.py" running
- [ ] No errors about "pip: command not found" or "index.js"

## Troubleshooting

### Still seeing "pip: command not found"?

**Problem:** Root Directory not set to `bot`

**Solution:**
1. Railway Settings → Root Directory → `bot` → Save
2. Redeploy

### Still seeing "node_modules" in build logs?

**Problem:** Railway still detecting as Node.js

**Solution:**
1. Verify Root Directory is `bot` (not empty, not `/`)
2. Verify Builder is "Dockerfile" (not "Nixpacks" or "Auto")
3. Delete the service and create a new one with Root Directory set from the start

### Build succeeds but bot doesn't respond?

**Problem:** Environment variables missing or incorrect

**Solution:**
1. Railway Variables tab → Verify all 3 variables exist
2. Check for typos in variable names (case-sensitive!)
3. Test Telegram token with @BotFather
4. Verify Convex URL is correct
5. Redeploy

## Summary

**Configuration files are ready** ✅ (Dockerfile, railway.json, .dockerignore)

**You must manually configure Railway Dashboard:**
1. Root Directory → `bot`
2. Builder → Dockerfile
3. Add 3 environment variables
4. Redeploy

---

**Next Action:** Go to Railway Dashboard and complete the 4 steps above.
