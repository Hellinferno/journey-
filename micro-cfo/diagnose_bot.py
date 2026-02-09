"""
Complete diagnostic check for Micro-CFO Bot
Run this before starting the bot to ensure everything is configured correctly
"""
import os
import sys
from dotenv import load_dotenv

print("=" * 70)
print("MICRO-CFO BOT DIAGNOSTIC CHECK")
print("=" * 70)

# Load environment
load_dotenv()

# Track issues
issues = []
warnings = []

# 1. Check Python Cache
print("\n1. Checking Python Cache...")
if os.path.exists("__pycache__") or os.path.exists("app/__pycache__"):
    warnings.append("Python cache exists - may use old code")
    print("   ⚠️  Cache folders found (will be cleared on fresh start)")
else:
    print("   ✅ No cache folders found")

# 2. Check Environment Variables
print("\n2. Checking Environment Variables...")
required_vars = {
    "TELEGRAM_TOKEN": "Telegram Bot Token",
    "CONVEX_URL": "Convex Backend URL",
    "GOOGLE_API_KEY": "Google Gemini API Key"
}

for var, description in required_vars.items():
    value = os.getenv(var)
    if value:
        # Show partial value for security
        if len(value) > 20:
            display = f"{value[:10]}...{value[-5:]}"
        else:
            display = f"{value[:5]}..."
        print(f"   ✅ {description}: {display}")
    else:
        issues.append(f"Missing {description} ({var})")
        print(f"   ❌ {description}: NOT FOUND")

# 3. Check AI Module
print("\n3. Checking AI Module...")
try:
    from app.ai import analyze_invoice
    import inspect
    source = inspect.getsource(analyze_invoice)
    
    if "gemini-2.5-flash" in source:
        print("   ✅ Using correct model: gemini-2.5-flash")
    elif "gemini-1.5-flash" in source:
        issues.append("AI module using old model (gemini-1.5-flash)")
        print("   ❌ Using OLD model: gemini-1.5-flash")
    else:
        warnings.append("Could not verify model name")
        print("   ⚠️  Could not verify model name")
except Exception as e:
    issues.append(f"Cannot import AI module: {e}")
    print(f"   ❌ Import failed: {e}")

# 4. Check Telegram Bot Module
print("\n4. Checking Telegram Bot Module...")
try:
    import telegram
    print(f"   ✅ python-telegram-bot installed (v{telegram.__version__})")
except Exception as e:
    issues.append(f"Telegram module not installed: {e}")
    print(f"   ❌ Not installed: {e}")

# 5. Check Gemini API
print("\n5. Checking Gemini API Connection...")
try:
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        # Quick test
        response = model.generate_content("Say 'OK' if you're working")
        if response.text:
            print("   ✅ Gemini API is working")
        else:
            warnings.append("Gemini API responded but with empty text")
            print("   ⚠️  API responded but with empty text")
    else:
        print("   ⚠️  Skipped (no API key)")
except Exception as e:
    issues.append(f"Gemini API test failed: {e}")
    print(f"   ❌ API test failed: {str(e)[:60]}...")

# 6. Check Convex
print("\n6. Checking Convex Connection...")
try:
    from convex import ConvexClient
    convex_url = os.getenv("CONVEX_URL")
    if convex_url:
        print(f"   ✅ Convex client available")
        print(f"   ℹ️  URL: {convex_url}")
    else:
        warnings.append("No Convex URL configured")
        print("   ⚠️  No Convex URL configured")
except Exception as e:
    issues.append(f"Convex module issue: {e}")
    print(f"   ❌ Issue: {e}")

# Summary
print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)

if not issues and not warnings:
    print("\n🎉 ALL CHECKS PASSED! Your bot is ready to run.")
    print("\nTo start the bot:")
    print("  1. Run: start_bot_fresh.bat")
    print("  2. Or run: python bot.py")
elif issues:
    print(f"\n❌ FOUND {len(issues)} CRITICAL ISSUE(S):")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    if warnings:
        print(f"\n⚠️  FOUND {len(warnings)} WARNING(S):")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    print("\n⚠️  Please fix the issues above before starting the bot.")
    sys.exit(1)
else:
    print(f"\n⚠️  FOUND {len(warnings)} WARNING(S):")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")
    print("\n✅ No critical issues found. Bot should work but check warnings.")
    print("\nTo start the bot:")
    print("  1. Run: start_bot_fresh.bat (recommended)")
    print("  2. Or run: python bot.py")

print("\n" + "=" * 70)
