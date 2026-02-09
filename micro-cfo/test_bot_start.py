"""Test if bot can start without errors"""
import sys
import os

print("=" * 60)
print("TESTING BOT STARTUP")
print("=" * 60)

try:
    # Test imports
    print("\n[1/5] Testing imports...")
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded")
    
    from telegram import Update
    from telegram.ext import ApplicationBuilder
    print("✅ telegram imports OK")
    
    from convex import ConvexClient
    print("✅ convex import OK")
    
    from app.ai import analyze_invoice
    print("✅ app.ai import OK")
    
    # Test environment
    print("\n[2/5] Testing environment...")
    token = os.getenv("TELEGRAM_TOKEN")
    if token:
        print(f"✅ TELEGRAM_TOKEN: {token[:10]}...")
    else:
        print("❌ TELEGRAM_TOKEN missing!")
        sys.exit(1)
    
    convex_url = os.getenv("CONVEX_URL")
    if convex_url:
        print(f"✅ CONVEX_URL: {convex_url}")
    else:
        print("❌ CONVEX_URL missing!")
        sys.exit(1)
    
    # Test Telegram connection
    print("\n[3/5] Testing Telegram connection...")
    app = ApplicationBuilder().token(token).build()
    print("✅ Telegram app built successfully")
    
    # Test Convex connection
    print("\n[4/5] Testing Convex connection...")
    client = ConvexClient(convex_url)
    print("✅ Convex client created")
    
    # Test AI module
    print("\n[5/5] Testing AI module...")
    import inspect
    source = inspect.getsource(analyze_invoice)
    if "gemini-2.5-flash" in source:
        print("✅ Using correct model: gemini-2.5-flash")
    else:
        print("❌ Wrong model in AI module!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Bot should start successfully")
    print("=" * 60)
    print("\nYou can now start the bot with:")
    print("  python bot.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
