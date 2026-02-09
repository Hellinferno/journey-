import re
from app.schemas import InvoiceData, ExpenseCategory
from typing import List


def validate_gstin(gstin: str) -> bool:
    """
    Validate GSTIN format: 15 chars, specific pattern
    Pattern: [0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}
    
    Args:
        gstin: GSTIN string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not gstin or len(gstin) != 15:
        return False
    
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    return bool(re.match(pattern, gstin))



def validate_gst_rate(total: float, tax: float) -> bool:
    """
    Check if tax rate matches standard GST rates
    
    Args:
        total: Total amount including tax
        tax: Tax amount
        
    Returns:
        True if rate matches standard rates (5%, 12%, 18%, 28%) with 0.5% tolerance
    """
    if total == 0:
        return True
    
    rate = (tax / (total - tax)) * 100
    standard_rates = [5, 12, 18, 28]
    
    # Allow 0.5% tolerance for rounding
    return any(abs(rate - std_rate) < 0.5 for std_rate in standard_rates)


def check_cash_limit(amount: float, payment_method: str = None) -> List[str]:
    """
    Check Section 40A(3) cash limit
    
    Args:
        amount: Transaction amount
        payment_method: Payment method (optional)
        
    Returns:
        List of compliance flags
    """
    flags = []
    
    # For now, we warn on all high-value transactions
    # In production, would check actual payment method
    if amount > 10000:
        flags.append("⚠️ Section 40A(3): Cash payments > ₹10,000 are disallowed")
    
    return flags


def check_blocked_itc(category: ExpenseCategory) -> List[str]:
    """
    Check Section 17(5) blocked ITC categories
    
    Args:
        category: Expense category
        
    Returns:
        List of compliance flags
    """
    flags = []
    
    blocked_categories = {
        ExpenseCategory.FOOD_BEVERAGE: "Section 17(5): Food & Beverage ITC generally blocked",
    }
    
    if category in blocked_categories:
        flags.append(f"🚫 {blocked_categories[category]}")
    
    return flags


def check_math(invoice: InvoiceData) -> List[str]:
    """
    Verify tax calculations
    
    Args:
        invoice: Invoice data to validate
        
    Returns:
        List of warning flags
    """
    warnings = []
    
    if invoice.total_amount > 0 and invoice.tax_amount > 0:
        if not validate_gst_rate(invoice.total_amount, invoice.tax_amount):
            warnings.append("⚠️ Tax rate doesn't match standard GST rates (5%, 12%, 18%, 28%)")
    
    return warnings


class HardRulesValidator:
    """Orchestrates all hard rule validations"""
    
    def validate(self, invoice: InvoiceData) -> dict:
        """
        Run all hard rules and return results
        
        Args:
            invoice: Invoice data to validate
            
        Returns:
            Dictionary with status and flags
        """
        flags = []
        status = "compliant"
        
        # GSTIN validation
        if invoice.gstin and not validate_gstin(invoice.gstin):
            flags.append("❌ Invalid GSTIN format")
            status = "review_needed"
        
        # Math validation
        math_flags = check_math(invoice)
        if math_flags:
            flags.extend(math_flags)
            status = "review_needed"
        
        # Cash limit check
        cash_flags = check_cash_limit(invoice.total_amount)
        if cash_flags:
            flags.extend(cash_flags)
            status = "review_needed"
        
        # Blocked ITC check
        itc_flags = check_blocked_itc(invoice.category)
        if itc_flags:
            flags.extend(itc_flags)
            status = "blocked"
        
        return {
            "status": status,
            "flags": flags,
        }

