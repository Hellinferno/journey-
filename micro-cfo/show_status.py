"""Show current bot status"""
import os
import sys
from datetime import datetime

print("=" * 70)
print("MICRO-CFO BOT STATUS")
print("=" * 70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Check if bot is running
bot_running = False
try:
    import psutil
    python_processes = [p for p in psutil.process_iter(['pid', 'name', 'cmdline']) 
                       if p.info['name'] == 'python.exe']
    bot_running = any('bot.py' in ' '.join(p.info['cmdline'] or []) 
                     for p in python_processes)
    
    if bot_running:
        print("🟢 BOT STATUS: RUNNING")
        for p in python_processes:
            if 'bot.py' in ' '.join(p.info['cmdline'] or []):
                print(f"   PID: {p.info['pid']}")
    else:
        print("🔴 BOT STATUS: NOT RUNNING")
except:
    print("⚪ BOT STATUS: UNKNOWN (install psutil to check)")

print()

# Check model configuration
try:
    if 'app.ai' in sys.modules:
        del sys.modules['app.ai']
    from app.ai import analyze_invoice
    import inspect
    source = inspect.getsource(analyze_invoice)
    
    if "gemini-2.5-flash" in source:
        print("✅ MODEL: gemini-2.5-flash (CORRECT)")
    elif "gemini-1.5-flash" in source:
        print("❌ MODEL: gemini-1.5-flash (WRONG - OLD VERSION)")
    else:
        print("⚠️  MODEL: Unknown")
except Exception as e:
    print(f"❌ MODEL CHECK FAILED: {e}")

print()

# Check cache
cache_exists = os.path.exists("__pycache__") or os.path.exists("app/__pycache__")
if cache_exists:
    print("⚠️  CACHE: Exists (may cause issues)")
else:
    print("✅ CACHE: Cleared")

print()

# Check environment
from dotenv import load_dotenv
load_dotenv()

env_ok = True
for var in ["TELEGRAM_TOKEN", "GOOGLE_API_KEY", "CONVEX_URL"]:
    if os.getenv(var):
        print(f"✅ {var}: Set")
    else:
        print(f"❌ {var}: Missing")
        env_ok = False

print()
print("=" * 70)

if not bot_running and not cache_exists and env_ok:
    print("✅ READY TO START")
    print()
    print("Run: START_BOT_CLEAN.bat")
elif bot_running:
    print("⚠️  BOT IS ALREADY RUNNING")
    print()
    print("If it's not responding:")
    print("1. Run: STOP_BOT.bat")
    print("2. Then run: START_BOT_CLEAN.bat")
else:
    print("⚠️  ISSUES DETECTED - See above")

print("=" * 70)
