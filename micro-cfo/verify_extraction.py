
import os
import asyncio
from app.ai import analyze_invoice

async def test():
    image_path = "temp_invoice.jpg"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    print(f"Testing extraction on {image_path}...")
    try:
        data = analyze_invoice(image_path)
        print("\nSUCCESS! Extraction result:")
        print(f"Vendor: {data.vendor_name}")
        print(f"Amount: {data.total_amount}")
        print(f"Date: {data.date}")
        print(f"GSTIN: {data.gstin}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nFAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(test())
