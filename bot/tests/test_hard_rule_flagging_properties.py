"""
Property-based tests for hard rule violation flagging
Feature: rag-compliance-engine
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings, assume
from app.rules import HardRulesValidator
from app.schemas import InvoiceData, ExpenseCategory


# Strategy for generating invoice data
def invoice_strategy():
    """Generate arbitrary invoice data for property testing."""
    return st.builds(
        InvoiceData,
        vendor_name=st.text(min_size=1, max_size=50),
        invoice_number=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
        date=st.one_of(st.none(), st.text(min_size=10, max_size=10)),
        total_amount=st.floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
        tax_amount=st.floats(min_value=0.0, max_value=100000.0, allow_nan=False, allow_infinity=False),
        gstin=st.one_of(st.none(), st.text(min_size=0, max_size=20)),
        currency=st.just("INR"),
        category=st.sampled_from(list(ExpenseCategory)),
        item_description=st.text(min_size=1, max_size=100)
    )


# Feature: rag-compliance-engine, Property 8: Hard Rule Violation Flagging
@given(invoice=invoice_strategy())
@settings(max_examples=200, deadline=None)
def test_hard_rule_violations_produce_flags(invoice):
    """
    Property 8: Hard Rule Violation Flagging
    
    For any hard rule that fails validation, the system SHALL add at least one
    descriptive flag to the compliance report explaining the violation.
    
    This property verifies that:
    1. If status is not "compliant", then flags list is non-empty
    2. Each flag is a non-empty string
    3. Flags are descriptive (contain meaningful text)
    
    Validates: Requirements 5.5
    """
    validator = HardRulesValidator()
    result = validator.validate(invoice)
    
    # Extract status and flags
    status = result.get("status")
    flags = result.get("flags", [])
    
    # Property: If status indicates a problem, there must be flags
    if status in ["review_needed", "blocked"]:
        assert len(flags) > 0, (
            f"Expected at least one flag when status is '{status}'.\n"
            f"Invoice: {invoice}\n"
            f"Status: {status}\n"
            f"Flags: {flags}"
        )
        
        # Each flag must be a non-empty string
        for flag in flags:
            assert isinstance(flag, str), (
                f"Expected flag to be a string.\n"
                f"Flag: {flag}\n"
                f"Type: {type(flag)}"
            )
            assert len(flag) > 0, (
                f"Expected flag to be non-empty.\n"
                f"Flag: {repr(flag)}"
            )
            # Flags should contain meaningful text (at least 10 characters)
            assert len(flag) >= 10, (
                f"Expected flag to be descriptive (at least 10 characters).\n"
                f"Flag: {flag}\n"
                f"Length: {len(flag)}"
            )
    
    # Property: If status is compliant, flags should be empty
    if status == "compliant":
        assert len(flags) == 0, (
            f"Expected no flags when status is 'compliant'.\n"
            f"Invoice: {invoice}\n"
            f"Status: {status}\n"
            f"Flags: {flags}"
        )


# Feature: rag-compliance-engine, Property 8: Hard Rule Violation Flagging (Invalid GSTIN)
@given(
    vendor_name=st.text(min_size=1, max_size=50),
    total_amount=st.floats(min_value=1.0, max_value=100000.0, allow_nan=False, allow_infinity=False),
    category=st.sampled_from(list(ExpenseCategory)),
    item_description=st.text(min_size=1, max_size=100),
    invalid_gstin=st.text(min_size=1, max_size=20)
)
@settings(max_examples=100, deadline=None)
def test_invalid_gstin_produces_flag(vendor_name, total_amount, category, item_description, invalid_gstin):
    """
    Property 8: Hard Rule Violation Flagging (Invalid GSTIN)
    
    For any invoice with an invalid GSTIN, the validator SHALL produce
    at least one flag mentioning GSTIN.
    
    Validates: Requirements 5.5
    """
    # Ensure GSTIN is invalid (not 15 chars or wrong pattern)
    valid_pattern = (
        len(invalid_gstin) == 15 and
        invalid_gstin[0:2].isdigit() and
        invalid_gstin[2:7].isupper() and invalid_gstin[2:7].isalpha() and
        invalid_gstin[7:11].isdigit() and
        invalid_gstin[11].isupper() and invalid_gstin[11].isalpha() and
        invalid_gstin[12] in '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' and
        invalid_gstin[13] == 'Z' and
        invalid_gstin[14] in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )
    assume(not valid_pattern)
    
    invoice = InvoiceData(
        vendor_name=vendor_name,
        total_amount=total_amount,
        tax_amount=0.0,
        gstin=invalid_gstin,
        category=category,
        item_description=item_description
    )
    
    validator = HardRulesValidator()
    result = validator.validate(invoice)
    
    flags = result.get("flags", [])
    
    # Should have at least one flag
    assert len(flags) > 0, (
        f"Expected at least one flag for invalid GSTIN.\n"
        f"GSTIN: {invalid_gstin}\n"
        f"Flags: {flags}"
    )
    
    # At least one flag should mention GSTIN
    gstin_mentioned = any("GSTIN" in flag or "gstin" in flag for flag in flags)
    assert gstin_mentioned, (
        f"Expected at least one flag to mention GSTIN.\n"
        f"GSTIN: {invalid_gstin}\n"
        f"Flags: {flags}"
    )


# Feature: rag-compliance-engine, Property 8: Hard Rule Violation Flagging (Non-Standard GST Rate)
@given(
    vendor_name=st.text(min_size=1, max_size=50),
    base_amount=st.floats(min_value=100.0, max_value=100000.0, allow_nan=False, allow_infinity=False),
    non_standard_rate=st.floats(min_value=1.0, max_value=50.0, allow_nan=False, allow_infinity=False),
    category=st.sampled_from(list(ExpenseCategory)),
    item_description=st.text(min_size=1, max_size=100)
)
@settings(max_examples=100, deadline=None)
def test_non_standard_gst_rate_produces_flag(vendor_name, base_amount, non_standard_rate, category, item_description):
    """
    Property 8: Hard Rule Violation Flagging (Non-Standard GST Rate)
    
    For any invoice with a non-standard GST rate, the validator SHALL produce
    at least one flag mentioning tax rate or GST.
    
    Validates: Requirements 5.5
    """
    standard_rates = [5, 12, 18, 28]
    
    # Only test rates that are NOT within 0.5% of any standard rate
    is_near_standard = any(abs(non_standard_rate - std_rate) < 0.5 for std_rate in standard_rates)
    assume(not is_near_standard)
    
    # Calculate tax amount from non-standard rate
    tax_amount = base_amount * (non_standard_rate / 100)
    total_amount = base_amount + tax_amount
    
    invoice = InvoiceData(
        vendor_name=vendor_name,
        total_amount=total_amount,
        tax_amount=tax_amount,
        category=category,
        item_description=item_description
    )
    
    validator = HardRulesValidator()
    result = validator.validate(invoice)
    
    flags = result.get("flags", [])
    
    # Should have at least one flag
    assert len(flags) > 0, (
        f"Expected at least one flag for non-standard GST rate.\n"
        f"Rate: {non_standard_rate:.2f}%\n"
        f"Flags: {flags}"
    )
    
    # At least one flag should mention tax or GST or rate
    tax_mentioned = any(
        "tax" in flag.lower() or "gst" in flag.lower() or "rate" in flag.lower()
        for flag in flags
    )
    assert tax_mentioned, (
        f"Expected at least one flag to mention tax/GST/rate.\n"
        f"Rate: {non_standard_rate:.2f}%\n"
        f"Flags: {flags}"
    )


# Feature: rag-compliance-engine, Property 8: Hard Rule Violation Flagging (Cash Limit)
@given(
    vendor_name=st.text(min_size=1, max_size=50),
    high_amount=st.floats(min_value=10001.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    category=st.sampled_from(list(ExpenseCategory)),
    item_description=st.text(min_size=1, max_size=100)
)
@settings(max_examples=100, deadline=None)
def test_cash_limit_violation_produces_flag(vendor_name, high_amount, category, item_description):
    """
    Property 8: Hard Rule Violation Flagging (Cash Limit)
    
    For any invoice with amount > ₹10,000, the validator SHALL produce
    at least one flag mentioning Section 40A(3) or cash limit.
    
    Validates: Requirements 5.5
    """
    invoice = InvoiceData(
        vendor_name=vendor_name,
        total_amount=high_amount,
        tax_amount=0.0,
        category=category,
        item_description=item_description
    )
    
    validator = HardRulesValidator()
    result = validator.validate(invoice)
    
    flags = result.get("flags", [])
    
    # Should have at least one flag
    assert len(flags) > 0, (
        f"Expected at least one flag for high-value transaction.\n"
        f"Amount: ₹{high_amount:.2f}\n"
        f"Flags: {flags}"
    )
    
    # At least one flag should mention Section 40A(3) or cash
    cash_mentioned = any(
        "40A" in flag or "cash" in flag.lower() or "10,000" in flag or "10000" in flag
        for flag in flags
    )
    assert cash_mentioned, (
        f"Expected at least one flag to mention cash limit or Section 40A(3).\n"
        f"Amount: ₹{high_amount:.2f}\n"
        f"Flags: {flags}"
    )


# Feature: rag-compliance-engine, Property 8: Hard Rule Violation Flagging (Blocked ITC)
@given(
    vendor_name=st.text(min_size=1, max_size=50),
    total_amount=st.floats(min_value=1.0, max_value=100000.0, allow_nan=False, allow_infinity=False),
    item_description=st.text(min_size=1, max_size=100)
)
@settings(max_examples=100, deadline=None)
def test_blocked_itc_category_produces_flag(vendor_name, total_amount, item_description):
    """
    Property 8: Hard Rule Violation Flagging (Blocked ITC)
    
    For any invoice in the FOOD_BEVERAGE category, the validator SHALL produce
    at least one flag mentioning Section 17(5) or ITC or blocked.
    
    Validates: Requirements 5.5
    """
    invoice = InvoiceData(
        vendor_name=vendor_name,
        total_amount=total_amount,
        tax_amount=0.0,
        category=ExpenseCategory.FOOD_BEVERAGE,
        item_description=item_description
    )
    
    validator = HardRulesValidator()
    result = validator.validate(invoice)
    
    flags = result.get("flags", [])
    status = result.get("status")
    
    # Should have at least one flag
    assert len(flags) > 0, (
        f"Expected at least one flag for blocked ITC category.\n"
        f"Category: {ExpenseCategory.FOOD_BEVERAGE}\n"
        f"Flags: {flags}"
    )
    
    # Status should be blocked for ITC violations
    assert status == "blocked", (
        f"Expected status 'blocked' for blocked ITC category.\n"
        f"Category: {ExpenseCategory.FOOD_BEVERAGE}\n"
        f"Status: {status}"
    )
    
    # At least one flag should mention Section 17(5) or ITC or blocked
    itc_mentioned = any(
        "17(5)" in flag or "ITC" in flag or "blocked" in flag.lower()
        for flag in flags
    )
    assert itc_mentioned, (
        f"Expected at least one flag to mention ITC/Section 17(5)/blocked.\n"
        f"Category: {ExpenseCategory.FOOD_BEVERAGE}\n"
        f"Flags: {flags}"
    )


# Feature: rag-compliance-engine, Property 8: Hard Rule Violation Flagging (Multiple Violations)
@given(
    vendor_name=st.text(min_size=1, max_size=50),
    high_amount=st.floats(min_value=10001.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    item_description=st.text(min_size=1, max_size=100),
    invalid_gstin=st.text(min_size=1, max_size=14)  # Invalid length
)
@settings(max_examples=100, deadline=None)
def test_multiple_violations_produce_multiple_flags(vendor_name, high_amount, item_description, invalid_gstin):
    """
    Property 8: Hard Rule Violation Flagging (Multiple Violations)
    
    For any invoice with multiple hard rule violations, the validator SHALL produce
    multiple flags (one for each violation).
    
    Validates: Requirements 5.5
    """
    invoice = InvoiceData(
        vendor_name=vendor_name,
        total_amount=high_amount,
        tax_amount=0.0,
        gstin=invalid_gstin,
        category=ExpenseCategory.FOOD_BEVERAGE,
        item_description=item_description
    )
    
    validator = HardRulesValidator()
    result = validator.validate(invoice)
    
    flags = result.get("flags", [])
    
    # Should have multiple flags (at least 2: invalid GSTIN, cash limit, blocked ITC)
    assert len(flags) >= 2, (
        f"Expected at least 2 flags for multiple violations.\n"
        f"GSTIN: {invalid_gstin}\n"
        f"Amount: ₹{high_amount:.2f}\n"
        f"Category: {ExpenseCategory.FOOD_BEVERAGE}\n"
        f"Flags: {flags}\n"
        f"Flag count: {len(flags)}"
    )


# Feature: rag-compliance-engine, Property 8: Hard Rule Violation Flagging (Compliant Invoice)
@given(
    vendor_name=st.text(min_size=1, max_size=50),
    low_amount=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    category=st.sampled_from([
        ExpenseCategory.OFFICE_SUPPLIES,
        ExpenseCategory.ELECTRONICS,
        ExpenseCategory.UTILITIES
    ]),
    item_description=st.text(min_size=1, max_size=100)
)
@settings(max_examples=100, deadline=None)
def test_compliant_invoice_produces_no_flags(vendor_name, low_amount, category, item_description):
    """
    Property 8: Hard Rule Violation Flagging (Compliant Invoice)
    
    For any invoice that passes all hard rules, the validator SHALL produce
    no flags and status should be "compliant".
    
    Validates: Requirements 5.5
    """
    invoice = InvoiceData(
        vendor_name=vendor_name,
        total_amount=low_amount,
        tax_amount=0.0,
        gstin=None,  # No GSTIN to validate
        category=category,
        item_description=item_description
    )
    
    validator = HardRulesValidator()
    result = validator.validate(invoice)
    
    flags = result.get("flags", [])
    status = result.get("status")
    
    # Should have no flags
    assert len(flags) == 0, (
        f"Expected no flags for compliant invoice.\n"
        f"Invoice: {invoice}\n"
        f"Flags: {flags}"
    )
    
    # Status should be compliant
    assert status == "compliant", (
        f"Expected status 'compliant' for compliant invoice.\n"
        f"Invoice: {invoice}\n"
        f"Status: {status}"
    )


if __name__ == "__main__":
    # Run the test manually
    import pytest
    pytest.main([__file__, "-v"])
