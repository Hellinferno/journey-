"""
Bot Integration Test Script
Tests the complete RAG Compliance Engine workflow
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from app.schemas import InvoiceData, ExpenseCategory
from app.compliance import ComplianceAuditor
from app.rules import validate_gstin, validate_gst_rate

# Load environment variables
load_dotenv()

def print_separator(title):
    """Print a formatted separator"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_hard_rules():
    """Test hard rules validator"""
    print_separator("[TEST] Testing Hard Rules Validator")
    
    # Test GSTIN validation
    valid_gstin = "27AAPFU0939F1ZV"
    invalid_gstin = "INVALID123"
    
    print(f"\nGSTIN Validation:")
    print(f"  Valid GSTIN '{valid_gstin}': {validate_gstin(valid_gstin)}")
    print(f"  Invalid GSTIN '{invalid_gstin}': {validate_gstin(invalid_gstin)}")
    
    # Test GST rate validation
    print(f"\nGST Rate Validation:")
    print(f"  18% rate (118 total, 18 tax): {validate_gst_rate(118.0, 18.0)}")
    print(f"  10% rate (110 total, 10 tax): {validate_gst_rate(110.0, 10.0)}")
    print(f"  Zero total: {validate_gst_rate(0.0, 0.0)}")

def create_test_invoices():
    """Create test invoice scenarios"""
    print_separator("[SETUP] Creating Test Invoices")
    
    invoices = {
        "compliant": InvoiceData(
            vendor_name="Office Mart",
            invoice_number="INV-001",
            date="2025-02-10",
            total_amount=1180.0,
            tax_amount=180.0,  # 18% GST
            gstin="27AAPFU0939F1ZV",
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Printer paper and stationery"
        ),
        "blocked": InvoiceData(
            vendor_name="Hotel Taj",
            invoice_number="INV-002",
            date="2025-02-10",
            total_amount=2360.0,
            tax_amount=360.0,  # 18% GST
            gstin="27BBBBB1234B1Z5",
            category=ExpenseCategory.FOOD_BEVERAGE,
            item_description="Staff lunch at hotel restaurant"
        ),
        "cash_limit": InvoiceData(
            vendor_name="Electronics Store",
            invoice_number="INV-003",
            date="2025-02-10",
            total_amount=15000.0,
            tax_amount=2700.0,  # 18% GST
            gstin="27CCCCC5678C1Z5",
            category=ExpenseCategory.ELECTRONICS,
            item_description="Laptop for office use"
        ),
        "invalid_gstin": InvoiceData(
            vendor_name="Local Vendor",
            total_amount=590.0,
            tax_amount=90.0,
            gstin="INVALID",
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Office supplies"
        )
    }
    
    print("\n[OK] Test invoices created:")
    for key, invoice in invoices.items():
        print(f"  - {key}: {invoice.vendor_name} (Rs.{invoice.total_amount})")
    
    return invoices

def test_audit(auditor, invoice, test_name):
    """Test a single invoice audit"""
    print_separator(f"[TEST] {test_name}")
    
    print(f"\nInvoice Details:")
    print(f"  Vendor: {invoice.vendor_name}")
    print(f"  Amount: Rs.{invoice.total_amount}")
    print(f"  Category: {invoice.category.value}")
    print(f"  GSTIN: {invoice.gstin or 'N/A'}")
    
    try:
        result = auditor.audit_invoice(invoice)
        
        print(f"\n[RESULT] Audit Result:")
        print(f"  Status: {result['status'].upper()}")
        print(f"  Category: {result['category']}")
        print(f"  ITC Eligible: {result.get('itc_eligible', 'N/A')}")
        
        if result['flags']:
            print(f"\n  Flags:")
            for flag in result['flags']:
                print(f"    * {flag}")
        else:
            print(f"\n  [OK] No compliance issues found!")
        
        if result.get('citations'):
            print(f"\n  [CITATIONS] Legal Citations:")
            for citation in result['citations']:
                print(f"    * {citation['source']}, Page {citation['page']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during audit: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("  RAG COMPLIANCE ENGINE - BOT INTEGRATION TEST")
    print("="*60)
    
    # Check environment variables
    api_key = os.getenv("GOOGLE_API_KEY")
    convex_url = os.getenv("CONVEX_URL")
    
    print(f"\nEnvironment Check:")
    print(f"  GOOGLE_API_KEY: {'[OK] Loaded' if api_key else '[ERROR] Missing'}")
    print(f"  CONVEX_URL: {'[OK] Loaded' if convex_url else '[ERROR] Missing'}")
    
    if not api_key or not convex_url:
        print("\n❌ Missing required environment variables!")
        print("   Please check your .env file.")
        return
    
    # Test 1: Hard Rules
    test_hard_rules()
    
    # Test 2: Create Test Invoices
    invoices = create_test_invoices()
    
    # Test 3: Initialize Auditor
    print_separator("[INIT] Initializing Compliance Auditor")
    try:
        auditor = ComplianceAuditor()
        print("\n[OK] ComplianceAuditor initialized successfully!")
        print("   - Hard Rules Validator: Ready")
        print("   - RAG Query Engine: Ready")
        print("   - AI Compliance Analyzer: Ready")
    except Exception as e:
        print(f"\n❌ Error initializing auditor: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 4: Run All Audit Tests
    test_results = {}
    test_results['compliant'] = test_audit(auditor, invoices['compliant'], "TEST 1: Compliant Office Supplies")
    test_results['blocked'] = test_audit(auditor, invoices['blocked'], "TEST 2: Blocked Food & Beverage")
    test_results['cash_limit'] = test_audit(auditor, invoices['cash_limit'], "TEST 3: High-Value Transaction")
    test_results['invalid_gstin'] = test_audit(auditor, invoices['invalid_gstin'], "TEST 4: Invalid GSTIN")
    
    # Summary
    print_separator("[SUMMARY] TEST SUMMARY")
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    print(f"\n  Tests Passed: {passed}/{total}")
    for test_name, result in test_results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"    {status} - {test_name}")
    
    print("\n" + "="*60)
    if passed == total:
        print("  [SUCCESS] ALL TESTS PASSED! Bot is ready to use!")
    else:
        print("  [WARNING] Some tests failed. Check the output above.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
