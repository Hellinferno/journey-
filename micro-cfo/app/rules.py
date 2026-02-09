import re
from app.schemas import InvoiceData

def validate_gstin(gstin: str) -> bool:
    """Validates GSTIN format: 2 digits + 5 chars + 4 digits + 1 char + 1 char + Z + 1 char"""
    if not gstin:
        return True  # Missing GSTIN is valid for small vendors
    
    # Standard Regex for Indian GSTIN
    pattern = r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    return bool(re.match(pattern, gstin))

def check_math(invoice: InvoiceData) -> list[str]:
    """Checks if Tax seems logical (approx 5%, 12%, 18%, 28%)."""
    warnings = []
    
    if invoice.total_amount > 0 and invoice.tax_amount > 0:
        taxable_value = invoice.total_amount - invoice.tax_amount
        if taxable_value > 0:
            implied_rate = (invoice.tax_amount / taxable_value) * 100
            
            # Allow margin of error +/- 1%
            common_rates = [5, 12, 18, 28]
            is_valid_rate = any(abs(implied_rate - r) < 1.5 for r in common_rates)
            
            if not is_valid_rate:
                warnings.append(f"⚠️ Unusual Tax Rate: {implied_rate:.1f}% (Expected 5/12/18/28%)")
    
    # High Value Cash Transaction Check (Section 40A(3))
    # Assuming cash payment for now (can be refined later)
    if invoice.total_amount > 10000:
        warnings.append("⚠️ Cash Payment > ₹10k? Verify Section 40A(3) compliance.")
    
    return warnings
