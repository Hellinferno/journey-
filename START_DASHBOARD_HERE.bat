@echo off
echo ========================================
echo   MICRO-CFO DASHBOARD STARTER
echo ========================================
echo.
echo Starting the dashboard...
echo.

cd dashboard
start http://localhost:3000
npm run dev

pause
