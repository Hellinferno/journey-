# Manual Repository Restructuring Steps

## ⚠️ IMPORTANT: Read Before Starting

Your current structure:
```
journey/                    <-- Git root
├── micro-cfo/             <-- Bot folder
├── dashboard/             <-- Dashboard folder
└── ...
```

Target structure:
```
journey/                    <-- Git root (same)
├── bot/                   <-- Renamed from micro-cfo
├── dashboard/             <-- Already correct ✅
└── ...
```

## Step-by-Step Manual Process

### Step 1: Close Applications

**CRITICAL:** Close these before proceeding:
- [ ] Close VS Code completely (File → Exit)
- [ ] Stop bot if running (Ctrl+C in terminal)
- [ ] Stop dashboard if running (Ctrl+C in terminal)
- [ ] Close any terminals in the `micro-cfo/` or `dashboard/` folders

### Step 2: Verify Folders Are Not In Use

Open a NEW Command Prompt (not in VS Code) and run:
```cmd
cd D:\journey
dir
```

You should see `micro-cfo` folder.

### Step 3: Rename Folder

In the same Command Prompt:
```cmd
ren micro-cfo bot
```

If you get "Access Denied" or "The process cannot access the file":
1. Restart your computer
2. Open Command Prompt immediately (before opening VS Code)
3. Run the rename command again

### Step 4: Verify Rename

```cmd
dir
```

You should now see `bot` folder instead of `micro-cfo`.

### Step 5: Remove Duplicate Convex Folder

```cmd
rmdir /s /q bot\convex
```

This removes the duplicate Convex schema (dashboard/convex is the source of truth).

### Step 6: Update .gitignore

Open `.gitignore` in Notepad and replace its contents with:

```
# Python Bot
bot/__pycache__/
bot/.env
bot/.pytest_cache/
bot/.hypothesis/
bot/venv/
bot/.venv/

# Dashboard
dashboard/node_modules/
dashboard/.next/
dashboard/.env.local
dashboard/out/

# Convex
dashboard/convex/.env.local
dashboard/convex/node_modules/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Misc
*.log
.hypothesis/
```

Save and close.

### Step 7: Commit Changes

```cmd
git add -A
git commit -m "refactor: Restructure repository - rename micro-cfo to bot"
git push origin main
```

### Step 8: Verify Everything Works

**Test Bot:**
```cmd
cd bot
python bot.py
```

Should start without errors.

**Test Dashboard:**
```cmd
cd dashboard
npm run dev
```

Should open at http://localhost:3000

**Run Tests:**
```cmd
cd bot
pytest tests/ -v
```

All tests should pass.

## Alternative: Use File Explorer

If command line doesn't work:

1. **Close VS Code completely**
2. **Open File Explorer**
3. **Navigate to:** `D:\journey`
4. **Right-click** on `micro-cfo` folder
5. **Select "Rename"**
6. **Type:** `bot`
7. **Press Enter**

If you get an error:
- Close all applications
- Restart computer
- Try again immediately after restart

## After Restructuring

### Update Deployment Configs

**Railway (Bot):**
1. Go to Railway dashboard
2. Select your bot project
3. Settings → Root Directory: `bot`
4. Redeploy

**Vercel (Dashboard):**
1. Go to Vercel dashboard
2. Select your dashboard project
3. Settings → Root Directory: `dashboard`
4. Redeploy

### Update Import Paths (if needed)

The bot code should work as-is since we're just renaming the folder, not changing internal structure.

## Troubleshooting

### "Access Denied" Error

**Cause:** Folder is in use by another process

**Solutions:**
1. Close VS Code completely
2. Close all Command Prompts/PowerShell windows
3. Stop Python processes:
   ```cmd
   taskkill /F /IM python.exe
   ```
4. Stop Node processes:
   ```cmd
   taskkill /F /IM node.exe
   ```
5. Try rename again

### "The directory is not empty"

**Cause:** Git or other files are locked

**Solution:**
1. Restart computer
2. Open Command Prompt BEFORE opening VS Code
3. Run rename command immediately

### Rename Works But Git Shows Issues

**Solution:**
```cmd
git status
git add -A
git commit -m "refactor: Rename micro-cfo to bot"
```

## Success Checklist

After restructuring, verify:

- [ ] Folder renamed: `micro-cfo/` → `bot/`
- [ ] No `bot/convex/` folder (removed)
- [ ] `.gitignore` updated
- [ ] Changes committed to git
- [ ] Bot runs: `cd bot && python bot.py`
- [ ] Dashboard runs: `cd dashboard && npm run dev`
- [ ] Tests pass: `cd bot && pytest tests/`
- [ ] Railway config updated (root: `bot`)
- [ ] Vercel config updated (root: `dashboard`)

## Final Structure

After completion:
```
journey/
├── bot/                    ✅ Renamed from micro-cfo
│   ├── app/
│   ├── tests/
│   ├── bot.py
│   └── requirements.txt
├── dashboard/              ✅ Already correct
│   ├── convex/            ✅ Single source of truth
│   ├── src/
│   └── package.json
├── .kiro/
├── *.pdf
└── README.md
```

---

**Need help?** If you're stuck, provide:
- Error message you're seeing
- Which step you're on
- Screenshot of File Explorer showing current folders
