from app.schemas import InvoiceData, ExpenseCategory
from app.rules import validate_gstin, check_math

def audit_invoice(invoice: InvoiceData) -> dict:
    """Runs CA Audit Logic on the invoice."""
    flags = []
    status = "compliant"
    
    # 1. Hard Rule: GSTIN Validation
    if invoice.gstin and not validate_gstin(invoice.gstin):
        flags.append("❌ Invalid GSTIN Format")
        status = "review_needed"
    
    # 2. Hard Rule: Math Check
    math_flags = check_math(invoice)
    flags.extend(math_flags)
    
    # 3. Soft Rule: Section 17(5) Blocked Credits
    # Food & Beverage is generally blocked unless you are in the same business
    if invoice.category == ExpenseCategory.FOOD_BEVERAGE:
        flags.append("🚫 ITC Blocked: Food & Beverages (Sec 17(5))")
        status = "blocked"
    
    # 4. Soft Rule: Personal vs Business (Simple heuristic)
    if invoice.category == ExpenseCategory.OTHER and invoice.total_amount > 5000:
        flags.append("⚠️ Verify business purpose for 'Other' expense > ₹5k")
    
    return {
        "status": status,
        "flags": flags,
        "category": invoice.category
    }
