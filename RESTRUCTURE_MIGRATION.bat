@echo off
echo ========================================
echo   MICRO-CFO REPOSITORY RESTRUCTURING
echo ========================================
echo.
echo This script will reorganize the repository to match deployment architecture:
echo   - micro-cfo/ will be renamed to bot/
echo   - bot/convex/ will be removed (dashboard/convex/ is source of truth)
echo   - Documentation will be updated
echo.
echo IMPORTANT: Close all applications using these folders before proceeding!
echo   - Close VS Code
echo   - Stop Python processes
echo   - Stop Node processes
echo.
pause

echo.
echo Step 1: Checking if folders are in use...
echo.

REM Check if bot folder already exists
if exist "bot\" (
    echo ERROR: bot\ folder already exists!
    echo Please remove or rename it first.
    pause
    exit /b 1
)

echo Step 2: Renaming micro-cfo to bot...
echo.
ren "micro-cfo" "bot"
if errorlevel 1 (
    echo ERROR: Failed to rename micro-cfo to bot
    echo Make sure no applications are using the folder
    pause
    exit /b 1
)
echo ✓ Renamed micro-cfo to bot

echo.
echo Step 3: Removing duplicate bot/convex folder...
echo.
if exist "bot\convex\" (
    rmdir /s /q "bot\convex"
    echo ✓ Removed bot/convex (dashboard/convex is source of truth)
) else (
    echo ℹ bot/convex not found (already removed or doesn't exist)
)

echo.
echo Step 4: Updating .gitignore...
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
) > .gitignore.new

move /y .gitignore.new .gitignore
echo ✓ Updated .gitignore

echo.
echo Step 5: Git operations...
echo.
git add -A
git commit -m "refactor: Restructure repository for clean deployment

- Renamed micro-cfo/ to bot/ for clarity
- Removed bot/convex/ (dashboard/convex/ is single source of truth)
- Updated .gitignore for new structure
- Matches deployment architecture: bot/ → Railway, dashboard/ → Vercel"

echo.
echo ========================================
echo   RESTRUCTURING COMPLETE!
echo ========================================
echo.
echo New structure:
echo   journey/
echo   ├── bot/              ^<-- DEPLOYS TO RAILWAY
echo   │   ├── app/
echo   │   ├── tests/
echo   │   ├── bot.py
echo   │   └── requirements.txt
echo   ├── dashboard/        ^<-- DEPLOYS TO VERCEL
echo   │   ├── convex/       ^<-- Single source of truth
echo   │   ├── src/
echo   │   └── package.json
echo.
echo Next steps:
echo   1. Test bot locally: cd bot ^&^& python bot.py
echo   2. Test dashboard locally: cd dashboard ^&^& npm run dev
echo   3. Push to GitHub: git push origin main
echo   4. Deploy bot to Railway
echo   5. Deploy dashboard to Vercel
echo.
pause
