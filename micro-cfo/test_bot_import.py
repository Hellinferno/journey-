"""Test that bot imports the correct AI module"""
import sys
sys.path.insert(0, '.')

from app.ai import analyze_invoice
import inspect

# Get the source code of analyze_invoice
source = inspect.getsource(analyze_invoice)

print("Checking analyze_invoice function...")
print("=" * 60)

if "gemini-2.5-flash" in source:
    print("✅ CORRECT: Using gemini-2.5-flash")
elif "gemini-1.5-flash" in source:
    print("❌ ERROR: Still using gemini-1.5-flash (OLD VERSION)")
    print("\nThe bot is loading cached Python bytecode.")
    print("Solution: Delete __pycache__ folders and restart bot")
else:
    print("⚠️  WARNING: Model name not found in source")

print("=" * 60)
print("\nModel line from source:")
for line in source.split('\n'):
    if 'model_name=' in line:
        print(f"  {line.strip()}")
