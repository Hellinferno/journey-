"""
Property-based tests for GST rate validation
Feature: rag-compliance-engine
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings, assume
from app.rules import validate_gst_rate


# Feature: rag-compliance-engine, Property 7: GST Rate Validation
@given(
    base_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    gst_rate=st.sampled_from([5, 12, 18, 28])
)
@settings(max_examples=100, deadline=None)
def test_standard_gst_rates_accepted(base_amount, gst_rate):
    """
    Property 7: GST Rate Validation (Standard Rates)
    
    For any invoice with total_amount > 0 and tax_amount > 0, where the calculated
    tax rate is within 0.5% of one of the standard GST rates (5%, 12%, 18%, or 28%),
    the validator SHALL return True.
    
    Validates: Requirements 5.2
    """
    # Calculate tax amount from base amount and GST rate
    tax_amount = base_amount * (gst_rate / 100)
    total_amount = base_amount + tax_amount
    
    result = validate_gst_rate(total_amount, tax_amount)
    
    assert result == True, (
        f"Expected validate_gst_rate to return True for standard GST rate.\n"
        f"Base Amount: {base_amount}\n"
        f"Tax Amount: {tax_amount}\n"
        f"Total Amount: {total_amount}\n"
        f"GST Rate: {gst_rate}%\n"
        f"Calculated Rate: {(tax_amount / base_amount) * 100:.2f}%\n"
        f"Result: {result}"
    )


# Feature: rag-compliance-engine, Property 7: GST Rate Validation (Within Tolerance)
@given(
    base_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    gst_rate=st.sampled_from([5, 12, 18, 28]),
    tolerance_offset=st.floats(min_value=-0.49, max_value=0.49)
)
@settings(max_examples=100, deadline=None)
def test_rates_within_tolerance_accepted(base_amount, gst_rate, tolerance_offset):
    """
    Property 7: GST Rate Validation (Tolerance Boundary)
    
    For any invoice where the calculated tax rate is within 0.5% of a standard
    GST rate, the validator SHALL return True (testing the tolerance boundary).
    
    Validates: Requirements 5.2
    """
    # Calculate tax with slight offset to test tolerance
    adjusted_rate = gst_rate + tolerance_offset
    tax_amount = base_amount * (adjusted_rate / 100)
    total_amount = base_amount + tax_amount
    
    result = validate_gst_rate(total_amount, tax_amount)
    
    assert result == True, (
        f"Expected validate_gst_rate to return True for rate within tolerance.\n"
        f"Base Amount: {base_amount}\n"
        f"Tax Amount: {tax_amount}\n"
        f"Total Amount: {total_amount}\n"
        f"Standard GST Rate: {gst_rate}%\n"
        f"Adjusted Rate: {adjusted_rate:.2f}%\n"
        f"Tolerance Offset: {tolerance_offset:.2f}%\n"
        f"Result: {result}"
    )


# Feature: rag-compliance-engine, Property 7: GST Rate Validation (Non-Standard Rates)
@given(
    base_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    non_standard_rate=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_non_standard_rates_rejected(base_amount, non_standard_rate):
    """
    Property 7: GST Rate Validation (Non-Standard Rates)
    
    For any invoice where the calculated tax rate is NOT within 0.5% of any
    standard GST rate (5%, 12%, 18%, 28%), the validator SHALL return False.
    
    Validates: Requirements 5.2
    """
    standard_rates = [5, 12, 18, 28]
    
    # Only test rates that are NOT within 0.5% of any standard rate
    is_near_standard = any(abs(non_standard_rate - std_rate) < 0.5 for std_rate in standard_rates)
    assume(not is_near_standard)
    
    # Calculate tax amount from non-standard rate
    tax_amount = base_amount * (non_standard_rate / 100)
    total_amount = base_amount + tax_amount
    
    result = validate_gst_rate(total_amount, tax_amount)
    
    assert result == False, (
        f"Expected validate_gst_rate to return False for non-standard GST rate.\n"
        f"Base Amount: {base_amount}\n"
        f"Tax Amount: {tax_amount}\n"
        f"Total Amount: {total_amount}\n"
        f"Non-Standard Rate: {non_standard_rate:.2f}%\n"
        f"Result: {result}"
    )


# Feature: rag-compliance-engine, Property 7: GST Rate Validation (Zero Total)
@given(tax_amount=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=50, deadline=None)
def test_zero_total_amount_accepted(tax_amount):
    """
    Property 7: GST Rate Validation (Zero Total Edge Case)
    
    For any invoice with total_amount = 0, the validator SHALL return True
    regardless of the tax amount (edge case handling).
    
    Validates: Requirements 5.2
    """
    total_amount = 0.0
    
    result = validate_gst_rate(total_amount, tax_amount)
    
    assert result == True, (
        f"Expected validate_gst_rate to return True for zero total amount.\n"
        f"Total Amount: {total_amount}\n"
        f"Tax Amount: {tax_amount}\n"
        f"Result: {result}"
    )


# Feature: rag-compliance-engine, Property 7: GST Rate Validation (Zero Tax)
@given(total_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=50, deadline=None)
def test_zero_tax_amount_rejected(total_amount):
    """
    Property 7: GST Rate Validation (Zero Tax)
    
    For any invoice with total_amount > 0 and tax_amount = 0, the calculated
    rate is 0%, which is not a standard GST rate, so validator SHALL return False.
    
    Validates: Requirements 5.2
    """
    tax_amount = 0.0
    
    result = validate_gst_rate(total_amount, tax_amount)
    
    assert result == False, (
        f"Expected validate_gst_rate to return False for zero tax amount.\n"
        f"Total Amount: {total_amount}\n"
        f"Tax Amount: {tax_amount}\n"
        f"Calculated Rate: 0%\n"
        f"Result: {result}"
    )


# Feature: rag-compliance-engine, Property 7: GST Rate Validation (Idempotence)
@given(
    total_amount=st.floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    tax_amount=st.floats(min_value=0.0, max_value=100000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_validation_idempotence(total_amount, tax_amount):
    """
    Property 7: GST Rate Validation (Idempotence)
    
    For any total and tax amounts, calling validate_gst_rate multiple times
    SHALL return the same result (validation is deterministic and idempotent).
    
    Validates: Requirements 5.2
    """
    result1 = validate_gst_rate(total_amount, tax_amount)
    result2 = validate_gst_rate(total_amount, tax_amount)
    result3 = validate_gst_rate(total_amount, tax_amount)
    
    assert result1 == result2 == result3, (
        f"Expected validate_gst_rate to return consistent results.\n"
        f"Total Amount: {total_amount}\n"
        f"Tax Amount: {tax_amount}\n"
        f"Results: {result1}, {result2}, {result3}"
    )


# Feature: rag-compliance-engine, Property 7: GST Rate Validation (Boundary Testing)
@given(
    base_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    gst_rate=st.sampled_from([5, 12, 18, 28]),
    boundary_offset=st.sampled_from([-0.51, -0.50, -0.49, 0.49, 0.50, 0.51])
)
@settings(max_examples=100, deadline=None)
def test_tolerance_boundary_behavior(base_amount, gst_rate, boundary_offset):
    """
    Property 7: GST Rate Validation (Tolerance Boundary Behavior)
    
    For rates exactly at or beyond the 0.5% tolerance boundary:
    - Rates within 0.5% (exclusive) SHALL be accepted
    - Rates at or beyond 0.5% SHALL be rejected
    
    Validates: Requirements 5.2
    """
    adjusted_rate = gst_rate + boundary_offset
    tax_amount = base_amount * (adjusted_rate / 100)
    total_amount = base_amount + tax_amount
    
    result = validate_gst_rate(total_amount, tax_amount)
    
    # Expected result based on tolerance
    expected = abs(boundary_offset) < 0.5
    
    assert result == expected, (
        f"Expected validate_gst_rate to return {expected} for boundary offset {boundary_offset}.\n"
        f"Base Amount: {base_amount}\n"
        f"Tax Amount: {tax_amount}\n"
        f"Total Amount: {total_amount}\n"
        f"Standard GST Rate: {gst_rate}%\n"
        f"Adjusted Rate: {adjusted_rate:.2f}%\n"
        f"Boundary Offset: {boundary_offset}%\n"
        f"Expected: {expected}\n"
        f"Result: {result}"
    )


if __name__ == "__main__":
    # Run the test manually
    import pytest
    pytest.main([__file__, "-v"])
