@echo off
echo ========================================
echo   MAJOR REPOSITORY RESTRUCTURING
echo ========================================
echo.
echo WARNING: This will completely reorganize your repository!
echo.
echo Current structure:
echo   journey/
echo   ├── micro-cfo/
echo   ├── dashboard/
echo   └── ...
echo.
echo Target structure:
echo   micro-cfo/ (git root)
echo   ├── bot/
echo   ├── dashboard/
echo   └── ...
echo.
echo This script will:
echo   1. Create a temporary 'bot' folder
echo   2. Move micro-cfo/* contents to bot/
echo   3. Remove empty micro-cfo folder
echo   4. Commit changes
echo.
echo CRITICAL: Make sure you have committed all changes first!
echo.
pause

echo.
echo Step 1: Stopping processes...
echo.
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Creating bot folder...
echo.
if exist "bot\" (
    echo ERROR: bot\ folder already exists!
    pause
    exit /b 1
)
mkdir bot
echo SUCCESS: Created bot folder

echo.
echo Step 3: Moving micro-cfo contents to bot...
echo.
xcopy "micro-cfo\*" "bot\" /E /I /H /Y
if errorlevel 1 (
    echo ERROR: Failed to copy files
    pause
    exit /b 1
)
echo SUCCESS: Copied files to bot

echo.
echo Step 4: Removing old micro-cfo folder...
echo.
rmdir /s /q "micro-cfo"
if errorlevel 1 (
    echo ERROR: Failed to remove micro-cfo
    echo You may need to remove it manually
    pause
    exit /b 1
)
echo SUCCESS: Removed micro-cfo folder

echo.
echo Step 5: Removing duplicate bot/convex...
echo.
if exist "bot\convex\" (
    rmdir /s /q "bot\convex"
    echo SUCCESS: Removed bot/convex
) else (
    echo INFO: bot/convex not found
)

echo.
echo Step 6: Updating .gitignore...
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
) > .gitignore
echo SUCCESS: Updated .gitignore

echo.
echo Step 7: Committing to git...
echo.
git add -A
git commit -m "refactor: Major restructure - flatten repository structure

- Moved micro-cfo/* contents to bot/
- Removed nested micro-cfo folder
- Removed bot/convex (dashboard/convex is source of truth)
- Updated .gitignore
- New structure: bot/ and dashboard/ at root level"

if errorlevel 1 (
    echo WARNING: Git commit failed
) else (
    echo SUCCESS: Changes committed
)

echo.
echo Step 8: Pushing to GitHub...
echo.
git push origin main
if errorlevel 1 (
    echo WARNING: Git push failed
    echo You may need to push manually
) else (
    echo SUCCESS: Pushed to GitHub
)

echo.
echo ========================================
echo   RESTRUCTURING COMPLETE!
echo ========================================
echo.
echo New structure:
echo   journey/ (or rename to micro-cfo/)
echo   ├── bot/              (Python bot)
echo   ├── dashboard/        (Next.js dashboard)
echo   ├── .kiro/
echo   └── ...
echo.
echo Next steps:
echo   1. Test bot: cd bot ^&^& python bot.py
echo   2. Test dashboard: cd dashboard ^&^& npm run dev
echo   3. Update Railway: Root Directory = bot
echo   4. Update Vercel: Root Directory = dashboard
echo.
pause
