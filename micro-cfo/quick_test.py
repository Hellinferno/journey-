"""Quick test to verify the bot will use the correct model"""
import sys
import os

# Force reload of modules
if 'app.ai' in sys.modules:
    del sys.modules['app.ai']
if 'app.schemas' in sys.modules:
    del sys.modules['app.schemas']

# Now import
from app.ai import analyze_invoice
import inspect

source = inspect.getsource(analyze_invoice)

print("=" * 60)
print("QUICK MODEL CHECK")
print("=" * 60)

if "gemini-2.5-flash" in source:
    print("✅ SUCCESS: Bot will use gemini-2.5-flash")
    print("\nYou can now start the bot with:")
    print("  START_BOT_CLEAN.bat")
    sys.exit(0)
elif "gemini-1.5-flash" in source:
    print("❌ ERROR: Bot is still using gemini-1.5-flash")
    print("\nThe app/ai.py file needs to be updated.")
    sys.exit(1)
else:
    print("⚠️  WARNING: Could not find model name in source")
    print("\nPlease check app/ai.py manually")
    sys.exit(1)
