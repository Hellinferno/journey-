@echo off
echo ========================================
echo   REPOSITORY RESTRUCTURING
echo ========================================
echo.
echo This will rename micro-cfo to bot
echo.
echo CRITICAL: This script will:
echo   1. Stop Python and Node processes
echo   2. Rename micro-cfo to bot
echo   3. Remove bot/convex (duplicate)
echo   4. Update .gitignore
echo   5. Commit and push changes
echo.
pause

echo.
echo Step 1: Stopping processes...
echo.
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Checking if bot folder exists...
echo.
if exist "bot\" (
    echo ERROR: bot\ folder already exists!
    echo Please remove it first or rename it.
    pause
    exit /b 1
)

echo.
echo Step 3: Renaming micro-cfo to bot...
echo.
ren "micro-cfo" "bot"
if errorlevel 1 (
    echo ERROR: Failed to rename folder
    echo The folder might still be in use.
    echo.
    echo Try these steps:
    echo 1. Close VS Code completely
    echo 2. Restart your computer
    echo 3. Run this script again
    pause
    exit /b 1
)
echo SUCCESS: Renamed micro-cfo to bot

echo.
echo Step 4: Removing duplicate bot/convex...
echo.
if exist "bot\convex\" (
    rmdir /s /q "bot\convex"
    if errorlevel 1 (
        echo WARNING: Could not remove bot\convex
        echo You may need to remove it manually
    ) else (
        echo SUCCESS: Removed bot/convex
    )
) else (
    echo INFO: bot/convex not found (already removed)
)

echo.
echo Step 5: Updating .gitignore...
echo.
(
echo # Python Bot
echo bot/__pycache__/
echo bot/.env
echo bot/.pytest_cache/
echo bot/.hypothesis/
echo bot/venv/
echo bot/.venv/
echo.
echo # Dashboard
echo dashboard/node_modules/
echo dashboard/.next/
echo dashboard/.env.local
echo dashboard/out/
echo.
echo # Convex
echo dashboard/convex/.env.local
echo dashboard/convex/node_modules/
echo.
echo # IDEs
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo.
echo # Misc
echo *.log
echo .hypothesis/
echo.
echo # Old structure
echo micro-cfo/
) > .gitignore

echo SUCCESS: Updated .gitignore

echo.
echo Step 6: Committing to git...
echo.
git add -A
git commit -m "refactor: Restructure repository - rename micro-cfo to bot

- Renamed micro-cfo/ to bot/ for clarity
- Removed bot/convex/ (dashboard/convex/ is single source of truth)
- Updated .gitignore for new structure
- Matches deployment architecture: bot/ -> Railway, dashboard/ -> Vercel"

if errorlevel 1 (
    echo WARNING: Git commit failed
    echo You may need to commit manually
) else (
    echo SUCCESS: Changes committed
)

echo.
echo Step 7: Pushing to GitHub...
echo.
git push origin main
if errorlevel 1 (
    echo WARNING: Git push failed
    echo You may need to push manually: git push origin main
) else (
    echo SUCCESS: Pushed to GitHub
)

echo.
echo ========================================
echo   RESTRUCTURING COMPLETE!
echo ========================================
echo.
echo New structure:
echo   journey/
echo   ├── bot/              (renamed from micro-cfo)
echo   ├── dashboard/        (unchanged)
echo   └── ...
echo.
echo Next steps:
echo   1. Test bot: cd bot ^&^& python bot.py
echo   2. Test dashboard: cd dashboard ^&^& npm run dev
echo   3. Update Railway: Settings -^> Root Directory: bot
echo   4. Update Vercel: Settings -^> Root Directory: dashboard
echo.
pause
