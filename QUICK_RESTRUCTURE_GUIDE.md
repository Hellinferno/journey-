# 🚀 Quick Restructure Guide

## The Problem
The `micro-cfo` folder is currently in use (probably by VS Code or Python), so we can't rename it right now.

## The Solution (Choose One)

### Option 1: Restart Computer (Easiest)

1. **Save all your work**
2. **Close all applications**
3. **Restart computer**
4. **After restart, open Command Prompt** (NOT VS Code yet)
5. **Run these commands:**
   ```cmd
   cd D:\journey
   ren micro-cfo bot
   rmdir /s /q bot\convex
   git add -A
   git commit -m "refactor: Rename micro-cfo to bot"
   git push origin main
   ```
6. **Done!** Now you can open VS Code

### Option 2: Force Close Processes (Faster)

1. **Close VS Code completely** (File → Exit)
2. **Open Command Prompt as Administrator**
3. **Run these commands:**
   ```cmd
   taskkill /F /IM python.exe
   taskkill /F /IM node.exe
   cd D:\journey
   ren micro-cfo bot
   rmdir /s /q bot\convex
   git add -A
   git commit -m "refactor: Rename micro-cfo to bot"
   git push origin main
   ```
4. **Done!**

### Option 3: Do It Later

You can continue working with the current structure (`micro-cfo/`) and restructure later when convenient. The system works fine as-is.

## After Restructuring

### Update Vercel
1. Go to Vercel Dashboard
2. Settings → General → Root Directory: `dashboard`
3. Settings → Environment Variables → Add: `NEXT_PUBLIC_CONVEX_URL`
4. Redeploy

### Update Railway (if deployed)
1. Go to Railway Dashboard
2. Settings → Root Directory: `bot`
3. Redeploy

## Why This Structure?

```
journey/
├── bot/              <-- Clear name, deploys to Railway
├── dashboard/        <-- Clear name, deploys to Vercel
└── ...
```

Benefits:
- ✅ Clear separation of concerns
- ✅ Each folder = one deployment
- ✅ Easy to understand
- ✅ Matches deployment architecture

## Current Priority

**For now, focus on fixing Vercel dashboard:**

1. Go to Vercel Dashboard
2. Settings → General → Root Directory: `dashboard`
3. Settings → Environment Variables:
   - Name: `NEXT_PUBLIC_CONVEX_URL`
   - Value: `https://woozy-chihuahua-345.convex.cloud`
   - Check all environments
4. Redeploy

**The folder rename can wait** - it's a nice-to-have, not critical for functionality.

---

**Bottom line:** Restart your computer, then run the rename commands. Or just fix Vercel first and restructure later.
