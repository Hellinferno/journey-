# 🔄 Repository Restructuring Instructions

## Quick Start

### Option 1: Automated (Recommended)

1. **Close all applications**:
   - Close VS Code
   - Stop any running Python processes
   - Stop any running Node processes

2. **Run the migration script**:
   ```cmd
   RESTRUCTURE_MIGRATION.bat
   ```

3. **Done!** The script will:
   - Rename `micro-cfo/` to `bot/`
   - Remove duplicate `bot/convex/`
   - Update `.gitignore`
   - Commit changes to git

### Option 2: Manual

If the automated script fails, follow these steps:

#### Step 1: Close Applications
- Close VS Code
- Stop Python: `Ctrl+C` in terminal running bot
- Stop Node: `Ctrl+C` in terminal running dashboard

#### Step 2: Rename Folder
```cmd
ren micro-cfo bot
```

#### Step 3: Remove Duplicate Convex
```cmd
rmdir /s /q bot\convex
```

#### Step 4: Update .gitignore
Add these lines to `.gitignore`:
```
# Python Bot
bot/__pycache__/
bot/.env
bot/.pytest_cache/

# Dashboard
dashboard/node_modules/
dashboard/.next/
dashboard/.env.local

# Convex
dashboard/convex/.env.local
```

#### Step 5: Commit Changes
```cmd
git add -A
git commit -m "refactor: Restructure repository for clean deployment"
git push origin main
```

## Verification

After restructuring, verify everything works:

### 1. Check Folder Structure
```cmd
dir
```

You should see:
- `bot/` (not `micro-cfo/`)
- `dashboard/`
- No `bot/convex/` folder

### 2. Test Bot
```cmd
cd bot
python bot.py
```

Should start without errors.

### 3. Test Dashboard
```cmd
cd dashboard
npm run dev
```

Should open at http://localhost:3000

### 4. Run Tests
```cmd
cd bot
pytest tests/ -v
```

All tests should pass.

## Update Deployment Configs

### Railway (Bot)

1. Go to Railway dashboard
2. Select your bot project
3. Update **Root Directory** to: `bot`
4. Redeploy

### Vercel (Dashboard)

1. Go to Vercel dashboard
2. Select your dashboard project
3. Update **Root Directory** to: `dashboard`
4. Redeploy

## Troubleshooting

### "Permission Denied" Error

**Cause**: Folder is in use by another process

**Solution**:
1. Close VS Code completely
2. Stop all Python processes: `taskkill /F /IM python.exe`
3. Stop all Node processes: `taskkill /F /IM node.exe`
4. Try again

### "Folder Already Exists" Error

**Cause**: `bot/` folder already exists

**Solution**:
```cmd
ren bot bot_old
ren micro-cfo bot
rmdir /s /q bot_old
```

### Git Errors

**Cause**: Uncommitted changes

**Solution**:
```cmd
git status
git add -A
git commit -m "WIP: Before restructure"
```

Then run migration script.

## Rollback

If something goes wrong:

```cmd
git reset --hard HEAD~1
git clean -fd
```

This will undo all changes.

## Post-Migration Checklist

- [ ] Folder renamed: `micro-cfo/` → `bot/`
- [ ] Duplicate removed: No `bot/convex/` folder
- [ ] `.gitignore` updated
- [ ] Changes committed to git
- [ ] Bot runs locally: `cd bot && python bot.py`
- [ ] Dashboard runs locally: `cd dashboard && npm run dev`
- [ ] Tests pass: `cd bot && pytest tests/`
- [ ] Railway deployment updated (root: `bot`)
- [ ] Vercel deployment updated (root: `dashboard`)
- [ ] Both services working in production

## Benefits After Restructuring

✅ **Clear Separation**: Bot and dashboard are independent
✅ **Single Source of Truth**: Convex schema in one place
✅ **Easy Deployment**: Each folder deploys independently
✅ **Better Organization**: Structure matches architecture
✅ **No Confusion**: Folder names match deployment targets

## Need Help?

1. Read `NEW_STRUCTURE_README.md` for detailed documentation
2. Check `RESTRUCTURE_PLAN.md` for technical details
3. Review deployment guides in each folder

---

**Ready to restructure? Run `RESTRUCTURE_MIGRATION.bat` now!**
