"""
Verification script to test invoice extraction with Gemini API.
"""
import os
import sys
from dotenv import load_dotenv
from app.ai import analyze_invoice

load_dotenv()

def main():
    # Check if API key is configured
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        sys.exit(1)
    
    print("✅ API Key found")
    print(f"   Key starts with: {api_key[:10]}...")
    
    # Check for test invoice image
    test_images = ["temp_invoice.jpg", "test_invoice.jpg", "invoice.jpg"]
    image_path = None
    
    for img in test_images:
        if os.path.exists(img):
            image_path = img
            break
    
    if not image_path:
        print("\n⚠️  No test invoice image found.")
        print("   Please add one of these files to test extraction:")
        for img in test_images:
            print(f"   - {img}")
        print("\n💡 To test with your own invoice:")
        print("   1. Save an invoice image as 'temp_invoice.jpg'")
        print("   2. Run: python verify_extraction.py")
        sys.exit(0)
    
    print(f"\n📸 Found test image: {image_path}")
    print("🔄 Testing invoice extraction...\n")
    
    try:
        result = analyze_invoice(image_path)
        print("\n✅ SUCCESS! Extraction completed:")
        print("=" * 50)
        print(f"Vendor Name:     {result.vendor_name}")
        print(f"Invoice Number:  {result.invoice_number or 'N/A'}")
        print(f"Date:            {result.date or 'N/A'}")
        print(f"Total Amount:    {result.currency} {result.total_amount}")
        print(f"Tax Amount:      {result.currency} {result.tax_amount}")
        print(f"GSTIN:           {result.gstin or 'N/A'}")
        print("=" * 50)
        print("\n🎉 Your Gemini API integration is working correctly!")
        
    except Exception as e:
        print(f"\n❌ EXTRACTION FAILED:")
        print(f"   Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Verify your GOOGLE_API_KEY has access to gemini-1.5-flash")
        print("   2. Check if the image is a valid invoice")
        print("   3. Ensure the image file is not corrupted")
        sys.exit(1)

if __name__ == "__main__":
    main()
